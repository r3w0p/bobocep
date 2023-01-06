# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from threading import RLock
from time import time
from types import MethodType
from typing import Callable, Optional

from bobocep.cep.gen.event.bobo_gen_event import \
    BoboGenEvent
from bobocep.cep.event.bobo_event import BoboEvent
from bobocep.cep.event.bobo_event_simple import BoboEventSimple
from bobocep.cep.gen.timestamp.bobo_gen_timestamp import BoboGenTimestamp
from bobocep.cep.gen.timestamp.bobo_gen_timestamp_epoch import \
    BoboGenTimestampEpoch


class BoboGenEventTime(BoboGenEvent):
    """An event generator that returns a BoboEventSimple time event if a given
    amount of time has elapsed. If the time has not elapsed, None is returned
    instead."""

    def __init__(self,
                 millis: int,
                 datagen: Optional[Callable] = None,
                 gen_timestamp: Optional[BoboGenTimestamp] = None,
                 from_now: bool = True,
                 tz=None):
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
