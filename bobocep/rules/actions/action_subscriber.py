from abc import ABC, abstractmethod

from bobocep.rules.events.action_event import ActionEvent


class IActionSubscriber(ABC):
    """An interface to subscribe to Action events."""

    @abstractmethod
    def on_action_attempt(self, event: ActionEvent):
        """
        When an action has been attempted.

        :param event: The action event.
        :type event: ActionEvent
        """
