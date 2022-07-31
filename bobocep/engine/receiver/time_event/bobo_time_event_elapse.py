# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from datetime import datetime
from time import time_ns
from types import MethodType
from typing import Union, Callable

from bobocep.engine.receiver.time_event.bobo_time_event import \
    BoboTimeEvent
from bobocep.event.bobo_event import BoboEvent
from bobocep.event.bobo_event_simple import BoboEventSimple


class BoboTimeEventElapse(BoboTimeEvent):

    def __init__(self,
                 milliseconds: int,
                 datagen: Callable,
                 from_now: bool = True,
                 tz=None):
        super().__init__()

        self._milliseconds = milliseconds
        self._datagen = datagen
        self._tz = tz
        self._last = self._time_ms() if from_now else 0

        # Prevent garbage collection of object if callable is a method.
        self._obj = datagen.__self__ \
            if isinstance(datagen, MethodType) else None

    def maybe_generate(self, event_id: str) -> Union[BoboEvent, None]:
        now = BoboTimeEventElapse._time_ms()
        if (now - self._last) > self._milliseconds:
            self._last = now
            return BoboEventSimple(
                event_id=event_id,
                timestamp=datetime.now(tz=self._tz),
                data=self._datagen())
        else:
            return None

    @staticmethod
    def _time_ms():
        return int(time_ns() / 1000)
