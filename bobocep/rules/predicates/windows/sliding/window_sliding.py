from abc import ABC, abstractmethod
from typing import List

from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.predicates.windows.bobo_predicate_window import \
    BoboPredicateWindow


class WindowSliding(BoboPredicateWindow, ABC):
    """A predicate that evaluates using a sliding time window.

    :param interval_ns: The sliding window time interval, in nanoseconds.
    :type interval_ns: int
    """

    def __init__(self, interval_ns: int) -> None:
        super().__init__()

        self._interval_ns = interval_ns

    @abstractmethod
    def get_previous_event(self, history: BoboHistory) -> BoboEvent:
        """Gets a previous event in the event history, for use in calculating
        the time interval between two events.

        :param history: The event history.
        :type history: BoboHistory

        :return: A historical event.
        """

    def evaluate(self,
                 event: BoboEvent,
                 history: BoboHistory,
                 recent: List[BoboEvent]) -> bool:
        event_history = self.get_previous_event(history)
        return (event.timestamp -
                event_history.timestamp) <= self._interval_ns
