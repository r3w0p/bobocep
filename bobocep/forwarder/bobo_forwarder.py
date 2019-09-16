from abc import ABC, abstractmethod
from queue import Queue

from bobocep.forwarder.forwarder_subscriber import IForwarderSubscriber
from bobocep.producer.producer_subscriber import IProducerSubscriber
from bobocep.rules.events.action_event import ActionEvent
from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.setup.task.bobo_task import BoboTask


class BoboForwarder(BoboTask,
                    IProducerSubscriber,
                    ABC):
    """A :code:`bobocep` event forwarder that forwards CompositeEvent
    instances.

    :param max_queue_size: The maximum data queue size,
                           defaults to 0 (infinite).
    :type max_queue_size: int, optional

    :param active: Whether task should start in an active state,
                   defaults to True.
    :type active: bool, optional
    """

    def __init__(self, max_queue_size: int = 0, active: bool = True) -> None:
        super().__init__(active=active)

        self._event_queue = Queue(maxsize=max_queue_size)
        self._subs = []

    @abstractmethod
    def _handle_forwarder_event(self, event: BoboEvent) -> bool:
        """
        Enables the forwarder to perform some action with the BoboEvent
        instance before it is sent to the subscribers of the forwarder.
        If the method returns True, the BoboEvent instance will be
        forwarded to subscribers.

        :param event: The event.
        :type event: BoboEvent

        :return: True if event was successfully handled, False otherwise.
        """

    def _loop(self) -> None:
        if not self._event_queue.empty():
            event = self._event_queue.get_nowait()

            if event is not None:
                if self._handle_forwarder_event(event):
                    for subscriber in self._subs:
                        subscriber.on_forwarder_success_event(event)
                else:
                    for subscriber in self._subs:
                        subscriber.on_forwarder_failure_event(event)

    def on_accepted_producer_event(self, event: CompositeEvent):
        if not self._is_cancelled:
            self._event_queue.put_nowait(event)

    def on_producer_action(self, event: ActionEvent) -> None:
        if not self._is_cancelled:
            self._event_queue.put_nowait(event)

    def subscribe(self, subscriber: IForwarderSubscriber) -> None:
        """
        :param subscriber: Subscribes to events from Forwarder.
        :type subscriber: IForwarderSubscriber
        """

        with self._lock:
            if not self._is_cancelled:
                if subscriber not in self._subs:
                    self._subs.append(subscriber)

    def unsubscribe(self, unsubscriber: IForwarderSubscriber) -> None:
        """
        :param unsubscriber: Unsubscribes to events from Forwarder.
        :type unsubscriber: IForwarderSubscriber
        """

        with self._lock:
            if unsubscriber in self._subs:
                self._subs.remove(unsubscriber)

    def on_rejected_producer_event(self, event: CompositeEvent):
        """"""

    def _setup(self) -> None:
        """"""

    def _cancel(self) -> None:
        """"""
