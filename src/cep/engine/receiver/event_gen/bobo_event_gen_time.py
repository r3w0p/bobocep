# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from datetime import datetime
from threading import RLock
from time import time
from types import MethodType
from typing import Callable, Optional

from src.cep.engine.receiver.event_gen.bobo_event_gen import \
    BoboEventGen
from src.cep.event.bobo_event import BoboEvent
from src.cep.event.bobo_event_simple import BoboEventSimple
from src.cep.event.timestamp_gen.bobo_timestamp_gen_epoch import \
    BoboTimestampGenEpoch


class BoboEventGenTime(BoboEventGen):
    """An event generator that returns a time event if a given amount of time
    has elapsed. Otherwise, None is returned."""

    def __init__(self,
                 milliseconds: int,
                 datagen: Callable,
                 from_now: bool = True,
                 tz=None):
        super().__init__()
        self._lock: RLock = RLock()

        self._milliseconds = milliseconds
        self._datagen = datagen
        self._tz = tz
        self._last = self._time_ms() if from_now else 0

        # Prevent garbage collection of object if callable is a method.
        self._obj = datagen.__self__ \
            if isinstance(datagen, MethodType) else None

    def maybe_generate(self, event_id: str) -> Optional[BoboEvent]:
        with self._lock:
            now = BoboEventGenTime._time_ms()
            if (now - self._last) > self._milliseconds:
                self._last = now
                return BoboEventSimple(
                    event_id=event_id,
                    timestamp=BoboTimestampGenEpoch.generate(),
                    data=self._datagen())
            else:
                return None

    @staticmethod
    def _time_ms() -> int:
        return round(time() * 1000)
