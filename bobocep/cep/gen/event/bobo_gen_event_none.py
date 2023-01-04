# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from typing import Optional

from bobocep.cep.gen.event.bobo_gen_event import \
    BoboGenEvent
from bobocep.cep.event.bobo_event import BoboEvent


class BoboGenEventNone(BoboGenEvent):
    """An event generator that always returns None."""

    def __init__(self):
        super().__init__()

    def maybe_generate(self, event_id: str) -> Optional[BoboEvent]:
        return None
