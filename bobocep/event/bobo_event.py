# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from abc import ABC
from datetime import datetime
from json import dumps
from typing import Any

from bobocep.event.bobo_event_error import BoboEventError


class BoboEvent(ABC):
    """An event."""

    _EXC_ID_LEN = "'event_id' must have a length greater than 0"

    def __init__(self,
                 event_id: str,
                 timestamp: datetime,
                 data: Any):
        super().__init__()

        if len(event_id) == 0:
            raise BoboEventError(self._EXC_ID_LEN)

        self.event_id = event_id
        self.timestamp = timestamp
        self.data = data

    def __str__(self) -> str:
        return dumps({
            "event_id": str(self.event_id),
            "timestamp": str(self.timestamp),
            "data": str(self.data)
        })
