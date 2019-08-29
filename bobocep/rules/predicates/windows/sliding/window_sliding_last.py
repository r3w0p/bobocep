from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.predicates.windows.sliding.window_sliding import \
    WindowSliding


class WindowSlidingLast(WindowSliding):
    """
    A predicate that evaluates using a sliding time window,
    where the window ranges from the last event in history to the next event.

    :param interval_sec: The sliding window time interval, in seconds.
    :type interval_sec: float
    """

    def __init__(self, interval_sec: float) -> None:
        super().__init__(interval_ns=int(interval_sec * 1e9))

    def get_previous_event(self, history: BoboHistory) -> BoboEvent:
        return history.last
