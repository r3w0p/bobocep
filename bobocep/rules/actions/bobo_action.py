from abc import abstractmethod

from bobocep.rules.actions.abstract_action import AbstractAction
from bobocep.rules.events.composite_event import CompositeEvent


class BoboAction(AbstractAction):
    """A :code:`bobocep` action."""

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def perform_action(self, event: CompositeEvent) -> bool:
        """
        Performs an action using the event provided.

        :param event: A composite event to use as part of the action process.
        :type event: CompositeEvent

        :return: True if the action was successful, False otherwise.
        """
