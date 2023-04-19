# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Complex event.
"""

from json import dumps, loads
from typing import Any

from bobocep.cep.event.event import BoboEventError, BoboEvent
from bobocep.cep.event.history import BoboHistory

_EXC_PRO_LEN = "phenomenon name must have a length greater than 0"
_EXC_PAT_LEN = "pattern name must have a length greater than 0"


class BoboEventComplex(BoboEvent):
    """
    A complex event.
    """

    TYPE_COMPLEX = "type_complex"

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
            raise BoboEventError(_EXC_PRO_LEN)

        if len(pattern_name) == 0:
            raise BoboEventError(_EXC_PAT_LEN)

        self._phenomenon_name: str = phenomenon_name
        self._pattern_name: str = pattern_name
        self._history: BoboHistory = history

    def cast(self, dtype: type) -> 'BoboEventComplex':
        """
        :param dtype: The type to which the event's data is cast.
        :return: A new BoboEventComplex instance with its data cast to `dtype`
            and all other properties identical to the original event.
        """
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
        """
        :return: Phenomenon name.
        """
        return self._phenomenon_name

    @property
    def pattern_name(self) -> str:
        """
        :return: Pattern name.
        """
        return self._pattern_name

    @property
    def history(self) -> BoboHistory:
        """
        :return: Event history.
        """
        return self._history

    def to_json_dict(self) -> dict:
        """
        :return: A JSON `dict` representation of the event.
        """
        return {
            self.EVENT_TYPE: self.TYPE_COMPLEX,
            self.EVENT_ID: self.event_id,
            self.TIMESTAMP: self.timestamp,
            self.DATA: self.data,
            self.PHENOMENON_NAME: self.phenomenon_name,
            self.PATTERN_NAME: self.pattern_name,
            self.HISTORY: self.history
        }

    def to_json_str(self) -> str:
        """
        :return: A JSON `str` representation of the event.
        """
        return dumps(self.to_json_dict(), default=lambda o: o.to_json_str())

    @staticmethod
    def from_json_str(j: str) -> 'BoboEventComplex':
        """
        :param j: A JSON `str` representation of the event.

        :return: A new instance of the event type.
        """
        return BoboEventComplex.from_json_dict(loads(j))

    @staticmethod
    def from_json_dict(d: dict) -> 'BoboEventComplex':
        """
        :param d: A JSON `dict` representation of the event.

        :return: A new instance of the event type.
        """
        return BoboEventComplex(
            event_id=d[BoboEventComplex.EVENT_ID],
            timestamp=d[BoboEventComplex.TIMESTAMP],
            data=d[BoboEventComplex.DATA],
            phenomenon_name=d[BoboEventComplex.PHENOMENON_NAME],
            pattern_name=d[BoboEventComplex.PATTERN_NAME],
            history=BoboHistory.from_json_str(d[BoboEventComplex.HISTORY])
        )

    def __str__(self) -> str:
        """
        :return: A JSON `str` representation of the event.
        """
        return self.to_json_str()
