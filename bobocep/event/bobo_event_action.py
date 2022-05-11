# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from datetime import datetime
from typing import Any

from bobocep.event.bobo_event import BoboEvent


class BoboEventAction(BoboEvent):
    """An action event."""

    def __init__(self,
                 event_id: str,
                 timestamp: datetime,
                 data: Any):
        super().__init__(
            event_id=event_id,
            timestamp=timestamp,
            data=data)

        # todo action event implementation
