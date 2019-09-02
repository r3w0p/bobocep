from time import time_ns
from typing import Dict
from threading import RLock

from bobocep.rules.actions.bobo_action import BoboAction
from bobocep.rules.events.composite_event import CompositeEvent


class RateLimitAction(BoboAction):
    """
    Ensures that CompositeEvent instances of a given name are only produced
    at a given rate i.e. one event with name *n* in *t* seconds.
    If multiple instances are created within the rate, the subsequence
    ones are dropped i.e. the action returns :code:`False`.

    :param limit_dict: Key-value pairs, where the key is the CompositeEvent
                       name and the value is the desired rate, in seconds.
    :type limit_dict: Dict[str, int]

    :param rate_other: The rate for all other events that have not been named,
                       defaults to 0.
    :type rate_other: int, optional
    """

    def __init__(self,
                 limit_dict: Dict[str, int],
                 rate_other: int = 0) -> None:
        super().__init__()

        self._limit_dict = limit_dict
        self._names = list(self._limit_dict.keys())
        self._rate_other = rate_other
        self._last = {}
        self._lock = RLock()

    def set_limit(self, name: str, limit: int) -> None:
        """
        :param name: The CompositeEvent name.
        :type name: str

        :param limit: The limit for the event.
        :type limit: int
        """

        with self._lock:
            self._limit_dict[name] = limit

            if name not in self._names:
                self._names.append(name)

    def perform_action(self, event: CompositeEvent) -> bool:
        with self._lock:
            name = event.name
            rate = self._limit_dict[name] if name in self._names \
                else self._rate_other

            if rate > 0:
                if name not in self._last:
                    self._last[name] = 0

                return (time_ns() - self._last[name]) / 1e-9 >= rate

            return True
