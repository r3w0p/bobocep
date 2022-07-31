# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from typing import Union

from bobocep.engine.receiver.time_event.bobo_time_event import \
    BoboTimeEvent
from bobocep.event.bobo_event import BoboEvent


class BoboTimeEventNone(BoboTimeEvent):

    def __init__(self):
        super().__init__()

    def maybe_generate(self, event_id: str) -> Union[BoboEvent, None]:
        return None
