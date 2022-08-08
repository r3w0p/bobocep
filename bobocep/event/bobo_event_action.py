# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from datetime import datetime
from typing import Any

from bobocep.event.bobo_event import BoboEvent
from bobocep.event.bobo_event_error import BoboEventError


class BoboEventAction(BoboEvent):
    """An action event."""

    _EXC_PRO_LEN = "'process_name' must have a length greater than 0"
    _EXC_PAT_LEN = "'pattern_name' must have a length greater than 0"
    _EXC_ACT_LEN = "'action_name' must have a length greater than 0"

    def __init__(self,
                 event_id: str,
                 timestamp: datetime,
                 data: Any,
                 process_name: str,
                 pattern_name: str,
                 action_name: str,
                 success: bool):
        super().__init__(
            event_id=event_id,
            timestamp=timestamp,
            data=data)

        if len(process_name) == 0:
            raise BoboEventError(self._EXC_PRO_LEN)

        if len(pattern_name) == 0:
            raise BoboEventError(self._EXC_PAT_LEN)

        if len(action_name) == 0:
            raise BoboEventError(self._EXC_ACT_LEN)

        self.process_name = process_name
        self.pattern_name = pattern_name
        self.action_name = action_name
        self.success = success
