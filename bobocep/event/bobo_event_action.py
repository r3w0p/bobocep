# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from datetime import datetime
from typing import Any

from bobocep.event.bobo_event import BoboEvent
from bobocep.event.bobo_event_error import BoboEventError


class BoboEventAction(BoboEvent):
    """An action event."""

    _EXC_ACT_LEN = "'action_name' must have a length greater than 0"

    def __init__(self,
                 event_id: str,
                 timestamp: datetime,
                 data: Any,
                 action_name: str,
                 success: bool):
        super().__init__(
            event_id=event_id,
            timestamp=timestamp,
            data=data)

        if len(action_name) == 0:
            raise BoboEventError(self._EXC_ACT_LEN)

        self.action_name = action_name
        self.success = success
