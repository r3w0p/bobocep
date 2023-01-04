# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from json import dumps, loads
from typing import Any

from bobocep.cep.event.bobo_event import BoboEvent
from bobocep.cep.event.bobo_event_error import BoboEventError
from bobocep.cep.event.bobo_history import BoboHistory


class BoboEventComplex(BoboEvent):
    """A complex event."""

    TYPE_COMPLEX = "complex"

    PROCESS_NAME = "process_name"
    PATTERN_NAME = "pattern_name"
    HISTORY = "history"

    _EXC_PRO_LEN = "process name must have a length greater than 0"
    _EXC_PAT_LEN = "pattern name must have a length greater than 0"

    def __init__(self,
                 event_id: str,
                 timestamp: int,
                 data: Any,
                 process_name: str,
                 pattern_name: str,
                 history: BoboHistory):
        super().__init__(
            event_id=event_id,
            timestamp=timestamp,
            data=data)

        if len(process_name) == 0:
            raise BoboEventError(self._EXC_PRO_LEN)

        if len(pattern_name) == 0:
            raise BoboEventError(self._EXC_PAT_LEN)

        self._process_name: str = process_name
        self._pattern_name: str = pattern_name
        self._history: BoboHistory = history

    @property
    def process_name(self) -> str:
        return self._process_name

    @property
    def pattern_name(self) -> str:
        return self._pattern_name

    @property
    def history(self) -> BoboHistory:
        return self._history

    def to_json_str(self) -> str:
        return dumps({
            self.EVENT_TYPE: self.TYPE_COMPLEX,
            self.EVENT_ID: self.event_id,
            self.TIMESTAMP: self.timestamp,
            self.DATA: str(self.data),
            self.PROCESS_NAME: self.process_name,
            self.PATTERN_NAME: self.pattern_name,
            self.HISTORY: self.history
        }, default=lambda o: o.to_json_str())

    @staticmethod
    def from_json_str(j: str) -> 'BoboEventComplex':
        return BoboEventComplex.from_dict(loads(j))

    @staticmethod
    def from_dict(d: dict) -> 'BoboEventComplex':
        return BoboEventComplex(
            event_id=d[BoboEventComplex.EVENT_ID],
            timestamp=d[BoboEventComplex.TIMESTAMP],
            data=d[BoboEventComplex.DATA],
            process_name=d[BoboEventComplex.PROCESS_NAME],
            pattern_name=d[BoboEventComplex.PATTERN_NAME],
            history=BoboHistory.from_json_str(d[BoboEventComplex.HISTORY])
        )
