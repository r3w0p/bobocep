from typing import List

from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.predicates.windows.bobo_predicate_window import \
    BoboPredicateWindow


class WindowFixed(BoboPredicateWindow):
    """A predicate that evaluates using a fixed time window.

    :param lower_ns: The lower bound of the fixed window, as Epoch timestamp
                     with nanosecond precision.
    :type lower_ns: int

    :param upper_ns: The upper bound of the fixed window, as Epoch timestamp
                     with nanosecond precision.
    :type upper_ns: int

    :raises RuntimeError: The lower bound is greater than or equal to the upper
                          bound.
    """

    def __init__(self, lower_ns: int, upper_ns: int) -> None:
        super().__init__()

        if lower_ns >= upper_ns:
            raise RuntimeError

        self._lower_ns = lower_ns
        self._upper_ns = upper_ns

    def evaluate(self,
                 event: BoboEvent,
                 history: BoboHistory,
                 recent: List[BoboEvent]) -> bool:
        return self._lower_ns <= event.timestamp <= self._upper_ns
