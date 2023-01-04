# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from json import dumps, loads
from typing import Any

from bobocep.cep.event.bobo_event import BoboEvent
from bobocep.cep.event.bobo_event_error import BoboEventError


class BoboEventAction(BoboEvent):
    """An action event."""

    TYPE_ACTION = "action"

    PROCESS_NAME = "process_name"
    PATTERN_NAME = "pattern_name"
    ACTION_NAME = "action_name"
    SUCCESS = "success"

    _EXC_PRO_LEN = "process name must have a length greater than 0"
    _EXC_PAT_LEN = "pattern name must have a length greater than 0"
    _EXC_ACT_LEN = "action name must have a length greater than 0"

    def __init__(self,
                 event_id,
                 timestamp: int,
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

        self._process_name: str = process_name
        self._pattern_name: str = pattern_name
        self._action_name: str = action_name
        self._success: bool = success

    @property
    def process_name(self) -> str:
        return self._process_name

    @property
    def pattern_name(self) -> str:
        return self._pattern_name

    @property
    def action_name(self) -> str:
        return self._action_name

    @property
    def success(self) -> bool:
        return self._success

    def to_json_str(self) -> str:
        return dumps({
            self.EVENT_TYPE: self.TYPE_ACTION,
            self.EVENT_ID: self.event_id,
            self.TIMESTAMP: self.timestamp,
            self.DATA: self.data,
            self.PROCESS_NAME: self.process_name,
            self.PATTERN_NAME: self.pattern_name,
            self.ACTION_NAME: self.action_name,
            self.SUCCESS: self.success
        }, default=lambda o: o.to_json_str())

    @staticmethod
    def from_json_str(j: str) -> 'BoboEventAction':
        return BoboEventAction.from_dict(loads(j))

    @staticmethod
    def from_dict(d: dict) -> 'BoboEventAction':
        return BoboEventAction(
            event_id=d[BoboEventAction.EVENT_ID],
            timestamp=d[BoboEventAction.TIMESTAMP],
            data=d[BoboEventAction.DATA],
            process_name=d[BoboEventAction.PROCESS_NAME],
            pattern_name=d[BoboEventAction.PATTERN_NAME],
            action_name=d[BoboEventAction.ACTION_NAME],
            success=d[BoboEventAction.SUCCESS]
        )
