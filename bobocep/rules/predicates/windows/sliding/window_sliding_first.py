from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.predicates.windows.sliding.window_sliding import \
    WindowSliding
from typing import List
from bobocep.rules.events.composite_event import CompositeEvent


class WindowSlidingFirst(WindowSliding):
    """
    A predicate that evaluates using a sliding time window,
    where the window ranges from the first event in history to the next event.

    :param interval_sec: The sliding window time interval, in seconds.
    :type interval_sec: float
    """

    def __init__(self, interval_sec: float) -> None:
        super().__init__(interval_ns=int(interval_sec * 1e9))

    def get_previous_event(self, history: BoboHistory) -> BoboEvent:
        return history.first
