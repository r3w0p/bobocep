# Copyright (c) 2022 The BoboCEP Authors
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from datetime import datetime
from time import time_ns
from typing import Union, Callable

from bobocep.engine.receiver.null_event.bobo_null_event import \
    BoboNullEvent
from bobocep.events.bobo_event import BoboEvent
from bobocep.events.bobo_event_primitive import BoboEventPrimitive


class BoboNullEventElapse(BoboNullEvent):

    def __init__(self,
                 milliseconds: int,
                 datagen=Callable,
                 tz=None):
        super().__init__()

        self._milliseconds = milliseconds
        self._datagen = datagen
        self._tz = tz
        self._last = 0

    def maybe_generate(self, event_id: str) -> Union[BoboEvent, None]:
        now = BoboNullEventElapse._time_ms()
        if (now - self._last) > self._milliseconds:
            self._last = now
            return BoboEventPrimitive(
                event_id=event_id,
                timestamp=datetime.now(tz=self._tz),
                data=self._datagen())
        else:
            return None

    @staticmethod
    def _time_ms():
        return int(time_ns() / 1000)
