# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from json import dumps, loads
from typing import Any

from bobocep.cep.event.event import BoboEventError, BoboEvent
from bobocep.cep.event.history import BoboHistory
from bobocep.cep.event.constants import *


class BoboEventComplex(BoboEvent):
    """
    A complex event.
    """

    TYPE_COMPLEX = "complex"

    PHENOMENON_NAME = "phenomenon_name"
    PATTERN_NAME = "pattern_name"
    HISTORY = "history"

    def __init__(self,
                 event_id: str,
                 timestamp: int,
                 data: Any,
                 phenomenon_name: str,
                 pattern_name: str,
                 history: BoboHistory):
        """
        :param event_id: The event ID.
        :param timestamp: The event timestamp.
        :param data: The event data.
        :param phenomenon_name: The phenomenon name.
        :param pattern_name: The pattern name.
        :param history: The history of events.

        :raises BoboEventError: If length of phenomenon name is equal to 0.
        :raises BoboEventError: If length of pattern name is equal to 0.
        """
        super().__init__(
            event_id=event_id,
            timestamp=timestamp,
            data=data)

        if len(phenomenon_name) == 0:
            raise BoboEventError(EXC_PRO_LEN)

        if len(pattern_name) == 0:
            raise BoboEventError(EXC_PAT_LEN)

        self._phenomenon_name: str = phenomenon_name
        self._pattern_name: str = pattern_name
        self._history: BoboHistory = history

    def cast(self, dtype: type) -> 'BoboEventComplex':
        return BoboEventComplex(
            event_id=self._event_id,
            timestamp=self._timestamp,
            data=dtype(self._data),
            phenomenon_name=self._phenomenon_name,
            pattern_name=self._pattern_name,
            history=self._history
        )

    @property
    def phenomenon_name(self) -> str:
        """Get phenomenon name."""
        return self._phenomenon_name

    @property
    def pattern_name(self) -> str:
        """Get pattern name."""
        return self._pattern_name

    @property
    def history(self) -> BoboHistory:
        """Get history."""
        return self._history

    def to_json_str(self) -> str:
        return dumps({
            self.EVENT_TYPE: self.TYPE_COMPLEX,
            self.EVENT_ID: self.event_id,
            self.TIMESTAMP: self.timestamp,
            self.DATA: self.data,
            self.PHENOMENON_NAME: self.phenomenon_name,
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
            phenomenon_name=d[BoboEventComplex.PHENOMENON_NAME],
            pattern_name=d[BoboEventComplex.PATTERN_NAME],
            history=BoboHistory.from_json_str(d[BoboEventComplex.HISTORY])
        )

    def __str__(self) -> str:
        return self.to_json_str()
