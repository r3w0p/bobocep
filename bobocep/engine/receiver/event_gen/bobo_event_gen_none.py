# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from typing import Optional

from bobocep.engine.receiver.event_gen.bobo_event_gen import \
    BoboEventGen
from bobocep.event.bobo_event import BoboEvent


class BoboEventGenNone(BoboEventGen):
    """An event generator that always returns None."""

    def __init__(self):
        super().__init__()

    def maybe_generate(self, event_id: str) -> Optional[BoboEvent]:
        return None
