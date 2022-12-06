# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from typing import Any

from src.cep.event.bobo_event import BoboEvent
from src.cep.event.bobo_event_error import BoboEventError
from src.cep.event.bobo_history import BoboHistory


class BoboEventComplex(BoboEvent):
    """A complex event."""

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

    def to_dict(self) -> dict:
        return {
            self.EVENT_TYPE: self.__class__.__name__,
            self.EVENT_ID: self.event_id,
            self.TIMESTAMP: self.timestamp,
            self.DATA: self.data,
            self.DATA_TYPE: type(self.data).__name__,
            self.PROCESS_NAME: self.process_name,
            self.PATTERN_NAME: self.pattern_name,
            self.HISTORY: self.history.to_dict()
        }

    @staticmethod
    def from_dict(d: dict) -> 'BoboEventComplex':
        BoboEventComplex.validate_dict(d, [
            (BoboEventComplex.EVENT_ID, str),
            (BoboEventComplex.TIMESTAMP, int),
            (BoboEventComplex.DATA, None),
            (BoboEventComplex.DATA_TYPE, str),
            (BoboEventComplex.PROCESS_NAME, str),
            (BoboEventComplex.PATTERN_NAME, str),
            (BoboEventComplex.HISTORY, dict)
        ])

        t = getattr(__builtins__, d[BoboEventComplex.DATA_TYPE])

        return BoboEventComplex(
            event_id=d[BoboEventComplex.EVENT_ID],
            timestamp=d[BoboEventComplex.TIMESTAMP],
            data=t(d[BoboEventComplex.DATA]),
            process_name=d[BoboEventComplex.PROCESS_NAME],
            pattern_name=d[BoboEventComplex.PATTERN_NAME],
            history=BoboHistory.from_dict(d[BoboEventComplex.HISTORY])
        )
