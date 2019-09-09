from abc import abstractmethod
from threading import RLock
from typing import Tuple, Optional

from bobocep.producer.producer_subscriber import IProducerSubscriber
from bobocep.rules.actions.abstract_action import AbstractAction
from bobocep.rules.actions.action_subscriber import IActionSubscriber
from bobocep.rules.events.composite_event import CompositeEvent


class BoboAction(AbstractAction,
                 IProducerSubscriber):
    """A :code:`bobocep` action that can execute some given task."""

    def __init__(self) -> None:
        super().__init__()

        self._subs = []
        self._lock = RLock()

    @abstractmethod
    def _perform_action(self, event: CompositeEvent) -> bool:
        """"""

    def execute(self,
                event: CompositeEvent) -> Tuple[bool, Optional[Exception]]:
        """
        Executes the action.

        :param event: A composite event to use as part of the action process.
        :type event: CompositeEvent

        :return: A Tuple containing the success of the action execution, and
                 any exception that was raised on failure, or None if an
                 exception is not raised.
        """

        with self._lock:
            success = False
            exception = None

            try:
                success = self._perform_action(event=event)
            except Exception as e:
                exception = e

            if success:
                self._notify_success(event=event)
            else:
                self._notify_failure(event=event, exception=exception)

            return success, exception

    def on_accepted_producer_event(self, event: CompositeEvent) -> None:
        self.execute(event=event)

    def on_rejected_producer_event(self, event: CompositeEvent) -> None:
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

    def _notify_success(self, event: CompositeEvent):
        for sub in self._subs:
            sub.on_action_success(event=event)

    def _notify_failure(self,
                        event: CompositeEvent,
                        exception: Exception = None):
        for sub in self._subs:
            sub.on_action_failure(event=event, exception=exception)
