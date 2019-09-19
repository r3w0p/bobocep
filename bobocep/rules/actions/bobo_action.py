from abc import abstractmethod
from threading import RLock

from bobocep.producer.producer_subscriber import IProducerSubscriber
from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.actions.action_subscriber import IActionSubscriber
from bobocep.rules.events.action_event import ActionEvent
from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.composite_event import CompositeEvent


class BoboAction(IProducerSubscriber):
    """A :code:`bobocep` action that can execute some given task.

    :param name: The action name, defaults to an empty string.
    :type name: str, optional
    """

    def __init__(self, name: str = None) -> None:
        super().__init__()

        self.name = name if name is not None else ""
        self._subs = []
        self._lock = RLock()

    @abstractmethod
    def _perform_action(self, event: BoboEvent) -> bool:
        """"""

    def execute(self, event: BoboEvent) -> ActionEvent:
        """
        Executes the action.

        :param event: An event to use as part of the action process.
        :type event: BoboEvent

        :return: A Tuple containing the success of the action execution, and
                 any exception that was raised on failure, or None if an
                 exception is not raised.
        """

        with self._lock:
            success = False
            exception = None
            description = None

            try:
                success = self._perform_action(event=event)
            except Exception as e:
                exception = type(e).__name__
                description = str(e)

            action_event = ActionEvent(
                timestamp=EpochNSClock.generate_timestamp(),
                name=self.name,
                success=success,
                for_event=event,
                exception=exception if exception is not None else None,
                description=description if description is not None else None
            )

            self._notify_action_attempt(event=action_event)
            return action_event

    def on_accepted_producer_event(self, event: CompositeEvent) -> None:
        self.execute(event=event)

    def on_rejected_producer_event(self, event: CompositeEvent) -> None:
        """"""

    def on_producer_action(self, event: ActionEvent):
        """"""

    def subscribe(self, subscriber: IActionSubscriber) -> None:
        """
        :param subscriber: Subscribes to events from the Action.
        :type subscriber: IActionSubscriber
        """

        with self._lock:
            if subscriber not in self._subs:
                self._subs.append(subscriber)

    def unsubscribe(self, unsubscriber: IActionSubscriber) -> None:
        """
        :param unsubscriber: Unsubscribes to events from the Action.
        :type unsubscriber: IActionSubscriber
        """

        with self._lock:
            if unsubscriber in self._subs:
                self._subs.remove(unsubscriber)

    def _notify_action_attempt(self, event: ActionEvent):
        for sub in self._subs:
            sub.on_action_attempt(event=event)
