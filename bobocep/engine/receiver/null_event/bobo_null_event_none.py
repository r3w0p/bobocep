# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from datetime import datetime
from time import time_ns
from typing import Union, Callable

from bobocep.engine.receiver.null_event.bobo_null_event import \
    BoboNullEvent
from bobocep.event.bobo_event import BoboEvent
from bobocep.event.bobo_event_simple import BoboEventSimple


class BoboNullEventNone(BoboNullEvent):

    def __init__(self):
        super().__init__()

    def maybe_generate(self, event_id: str) -> Union[BoboEvent, None]:
        return None
