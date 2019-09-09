from abc import ABC, abstractmethod

from bobocep.rules.events.composite_event import CompositeEvent


class IActionSubscriber(ABC):
    """An interface to subscribe to Action events."""

    @abstractmethod
    def on_action_success(self, event: CompositeEvent):
        """
        When an action is successful in its execution.

        :param event: The event used during action execution.
        :type event: CompositeEvent
        """

    @abstractmethod
    def on_action_failure(self,
                          event: CompositeEvent,
                          exception: Exception = None):
        """
        When an action is unsuccessful in its execution.

        :param event: The event used during action execution.
        :type event: CompositeEvent

        :param exception: An exception raised during action execution,
                          defaults to None.
        :type exception: Exception, optional
        """
