# Copyright (c) 2019-2024 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Generates BoboEvent objects.
"""

from abc import ABC, abstractmethod
from threading import RLock
from types import MethodType
from typing import Optional, Callable

from bobocep.cep.event import BoboEvent, BoboEventSimple
from bobocep.cep.gen.timestamp import BoboGenTimestamp, BoboGenTimestampEpoch


class BoboGenEvent(ABC):
    """
    An event generator.
    """

    @abstractmethod
    def maybe_generate(self, event_id: str) -> Optional[BoboEvent]:
        """
        :param event_id: The event ID to use in the generated event.
        :return: Either a generated BoboEvent instance or None.
        """


class BoboGenEventNone(BoboGenEvent):
    """
    An event generator that always returns None.
    """

    def maybe_generate(self, event_id: str) -> Optional[BoboEvent]:
        """
        :param event_id: An event ID (always ignored).
        :return: None.
        """
        return None


class BoboGenEventTime(BoboGenEvent):
    """
    An event generator that returns a BoboEventSimple time event if a given
    amount of time has elapsed. If the time has not elapsed, None is returned
    instead.
    """

    def __init__(self,
                 millis: int,
                 datagen: Optional[Callable] = None,
                 gen_timestamp: Optional[BoboGenTimestamp] = None,
                 from_now: bool = True,
                 tz=None):
        """
        :param millis: Milliseconds between event generations. Once the
            millisecond timer has elapsed, an event can be generated.
        :param datagen: Datagen to use in generated event.
        :param gen_timestamp: Custom timestamp generator.
            If None, a BoboGenTimestampEpoch instance is used to generate
            timestamps.
        :param from_now: If `True`, sets the millisecond timer to the current
            time; otherwise, the timer is set to 0.
        :param tz: Timezone data.
        """
        super().__init__()
        self._lock: RLock = RLock()

        self._millis: int = millis
        self._datagen: Optional[Callable] = datagen
        self._gen_ts_internal: BoboGenTimestampEpoch = BoboGenTimestampEpoch()
        self._tz = tz
        self._last: int = self._gen_ts_internal.generate() if from_now else 0
        self._gen_ts_event: BoboGenTimestamp = gen_timestamp \
            if gen_timestamp is not None else self._gen_ts_internal

        if self._datagen is not None:
            # Prevent garbage collection of object if callable is a method
            self._obj = datagen.__self__ \
                if isinstance(datagen, MethodType) else None

    def maybe_generate(self, event_id: str) -> Optional[BoboEvent]:
        """
        :param event_id: An event ID.
        :return: A BoboEventSimple instance if one is due to be generated,
            or `None` if not.
        """
        with self._lock:
            now = self._gen_ts_internal.generate()
            if (now - self._last) > self._millis:
                self._last = now
                return BoboEventSimple(
                    event_id=event_id,
                    timestamp=self._gen_ts_event.generate(),
                    data=self._datagen()
                    if self._datagen is not None else None)
            else:
                return None
