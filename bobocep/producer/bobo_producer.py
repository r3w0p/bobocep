from abc import ABC, abstractmethod
from queue import Queue

from bobocep.decider.decider_subscriber import IDeciderSubscriber
from bobocep.producer.abstract_producer import AbstractProducer
from bobocep.producer.producer_subscriber import IProducerSubscriber
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.setup.task.bobo_task import BoboTask


class BoboProducer(AbstractProducer,
                   BoboTask,
                   IDeciderSubscriber,
                   ABC):
    """A :code:`bobocep` event producer that creates CompositeEvent instances
    when a run reaches its final state.

    :param max_queue_size: The maximum data queue size,
                           defaults to 0 (infinite).
    :type max_queue_size: int, optional
    """

    def __init__(self, max_queue_size: int = 0) -> None:
        super().__init__()

        self._event_queue = Queue(maxsize=max_queue_size)
        self._subs = {}

    def _loop(self) -> None:
        while not self._event_queue.empty():
            event = self._event_queue.get_nowait()

            if event is not None:
                if self._handle_composite_event(event):
                    self._notify_accepted(event)
                else:
                    self._notify_rejected(event)

    @abstractmethod
    def _handle_composite_event(self, event: CompositeEvent) -> bool:
        """
        Enables the producer to perform some action with the CompositeEvent
        instance before it is sent to the subscribers of the producer.
        If the method returns True, the CompositeEvent instance will be
        forwarded to subscribers.

        :param event: The event.
        :type event: CompositeEvent

        :return: True if event was successfully handled, False otherwise.
        """

    def on_decider_complex_event(self, nfa_name: str, event: CompositeEvent):
        with self._lock:
            if not self._cancelled:
                self._event_queue.put_nowait(event)

    def subscribe(self,
                  event_name: str,
                  subscriber: IProducerSubscriber) -> None:
        """
        :param event_name: Subscribe to CompositeEvent instances which have
                           this name.
        :type event_name: str

        :param subscriber: Subscriber to events from Producer.
        :type subscriber: IProducerSubscriber
        """

        with self._lock:
            if not self._cancelled:
                if event_name not in self._subs:
                    self._subs[event_name] = []

                if subscriber not in self._subs[event_name]:
                    self._subs[event_name].append(subscriber)

    def unsubscribe(self,
                    event_name: str,
                    unsubscriber: IProducerSubscriber) -> None:
        """
        :param event_name: Unsubscribe to CompositeEvent instances which have
                           this name.
        :type event_name: str

        :param unsubscriber: Unsubscriber to events from Producer.
        :type unsubscriber: IProducerSubscriber
        """

        with self._lock:
            if event_name in self._subs:
                if unsubscriber in self._subs[event_name]:
                    self._subs[event_name].remove(unsubscriber)

    def _notify_accepted(self, event: CompositeEvent):
        for subscriber in self._subs[event.name]:
            subscriber.on_accepted_producer_event(event)

    def _notify_rejected(self, event: CompositeEvent):
        for subscriber in self._subs[event.name]:
            subscriber.on_rejected_producer_event(event)

    def _setup(self) -> None:
        """"""

    def _cancel(self) -> None:
        """"""
