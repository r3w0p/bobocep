from abc import abstractmethod

from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.predicates.abstract_predicate import AbstractPredicate


class BoboPredicate(AbstractPredicate):
    """A :code:`bobocep` predicate."""

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def evaluate(self, event: BoboEvent, history: BoboHistory) -> bool:
        """Evaluates the predicate.

        :param event: An event.
        :type event: BoboEvent

        :param history: A history of events.
        :type history: BoboHistory

        :return: True if the predicate evaluates to True,
                 False otherwise.
        :rtype: bool
        """
