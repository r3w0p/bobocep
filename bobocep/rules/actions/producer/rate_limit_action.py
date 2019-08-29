from time import time_ns
from typing import Dict

from bobocep.rules.actions.bobo_action import BoboAction
from bobocep.rules.events.composite_event import CompositeEvent


class RateLimitAction(BoboAction):
    """
    Ensures that CompositeEvent instances of a given name are only produced
    at a given rate i.e. one event with name *n* in *t* seconds.
    If multiple instances are created within the rate, the subsequence
    ones are dropped i.e. the action returns :code:`False`.

    :param pairs: Key-value pairs, where the key is the CompositeEvent name
                  and the value is the desired rate, in seconds.
    :type pairs: Dict[str, int]

    :param rate_other: The rate for all other events that are not specifically
                       named in pairs, defaults to 0.
    :type rate_other: int, optional
    """

    def __init__(self,
                 pairs: Dict[str, int],
                 rate_other: int = 0) -> None:
        super().__init__()

        self._pairs = pairs
        self._rate_other = rate_other
        self._names = self._pairs.keys()
        self._last = {}

    def perform_action(self, event: CompositeEvent) -> bool:
        name = event.name
        rate = self._pairs[name] if name in self._names else self._rate_other

        if rate > 0:
            if name not in self._last:
                self._last[name] = 0

            return (time_ns() - self._last[name]) / 1e-9 >= rate

        return True
