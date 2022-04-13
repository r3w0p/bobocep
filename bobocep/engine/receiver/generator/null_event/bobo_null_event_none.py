from typing import Union

from bobocep.engine.receiver.generator.null_event.bobo_null_event import \
    BoboNullEvent
from bobocep.events.bobo_event import BoboEvent


class BoboNullEventNone(BoboNullEvent):

    def __init__(self):
        super().__init__()

    def maybe_generate(self, event_id: str) -> Union[BoboEvent, None]:
        return None
