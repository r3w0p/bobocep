# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from datetime import datetime
from json import dumps
from typing import Any

from bobocep.event.bobo_event import BoboEvent


class BoboEventSimple(BoboEvent):
    """A simple event."""

    def __init__(self,
                 event_id: str,
                 timestamp: datetime,
                 data: Any):
        super().__init__(
            event_id=event_id,
            timestamp=timestamp,
            data=data)

    def __str__(self) -> str:
        return dumps({
            "event_id": str(self.event_id),
            "timestamp": str(self.timestamp),
            "data": str(self.data)
        })
