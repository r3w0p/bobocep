from threading import RLock
from typing import Dict

from bobocep.rules.actions.bobo_action import BoboAction
from bobocep.rules.events.composite_event import CompositeEvent


class RateLimitAction(BoboAction):
    """
    Ensures that CompositeEvent instances of a given name are only produced
    at a given rate i.e. one event with name *n* in *t* seconds.
    If multiple instances are created within the rate, the subsequence
    ones are dropped i.e. the action returns :code:`False`.

    :param name: The action name, defaults to an empty string.
    :type name: str, optional

    :param limit_dict: Key-value pairs, where the key is the CompositeEvent
                       name and the value is the desired rate, in seconds.
                       Defaults to an empty dict.
    :type limit_dict: Dict[str, int], optional

    :param rate_other: The rate for all other events that have not been named,
                       defaults to 0.
    :type rate_other: int, optional
    """

    def __init__(self,
                 name: str = None,
                 limit_dict: Dict[str, int] = None,
                 rate_other: int = 0) -> None:
        super().__init__(name=name)

        self._limit_dict = limit_dict if limit_dict is not None else {}
        self._names = list(self._limit_dict.keys())
        self._rate_other = rate_other
        self._last = {}
        self._lock = RLock()

    def get_limits(self) -> Dict[str, int]:
        """
        :return: A dict, where the keys are the names to limit and the
                 values are the desired rates for each name, in seconds.
        """
        with self._lock:
            return self._limit_dict.copy()

    def set_limit(self, name: str, rate: int) -> None:
        """
        :param name: The CompositeEvent name.
        :type name: str

        :param rate: The rate for the name.
        :type rate: int
        """

        with self._lock:
            self._limit_dict[name] = rate

            if name not in self._names:
                self._names.append(name)

    def _perform_action(self, event: CompositeEvent) -> bool:
        with self._lock:
            if isinstance(event, CompositeEvent):
                name = event.name
                rate = self._limit_dict[name] if name in self._names \
                    else self._rate_other

                if rate > 0:
                    if name not in self._last:
                        self._last[name] = 0

                    accept = (event.timestamp - self._last[name]) / 1e9 >= rate

                    if accept:
                        self._last[name] = event.timestamp

                    return accept
            return True
