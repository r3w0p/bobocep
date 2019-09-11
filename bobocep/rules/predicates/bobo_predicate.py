from abc import abstractmethod
from typing import List

from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory


class BoboPredicate:
    """A :code:`bobocep` predicate."""

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def evaluate(self,
                 event: BoboEvent,
                 history: BoboHistory,
                 recent: List[BoboEvent]) -> bool:
        """Evaluates the predicate.

        :param event: An event.
        :type event: BoboEvent

        :param history: A history of events.
        :type history: BoboHistory

        :param recent: Recently accepted complex events of the corresponding
                        automaton.
        :type recent: List[BoboEvent]

        :return: True if the predicate evaluates to True,
                 False otherwise.
        :rtype: bool
        """
