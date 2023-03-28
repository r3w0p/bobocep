# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from json import loads, dumps
from typing import Any

from bobocep.cep.event.event import BoboEvent


class BoboEventSimple(BoboEvent):
    """
    A simple event.
    """

    TYPE_SIMPLE = "simple"

    def __init__(self,
                 event_id: str,
                 timestamp: int,
                 data: Any):
        """
        :param event_id: The event ID.
        :param timestamp: The event timestamp.
        :param data: The event data.
        """
        super().__init__(
            event_id=event_id,
            timestamp=timestamp,
            data=data)

    def cast(self, dtype: type) -> 'BoboEventSimple':
        return BoboEventSimple(
            event_id=self._event_id,
            timestamp=self._timestamp,
            data=dtype(self._data)
        )

    def to_json_str(self) -> str:
        return dumps({
            self.EVENT_TYPE: self.TYPE_SIMPLE,
            self.EVENT_ID: self.event_id,
            self.TIMESTAMP: self.timestamp,
            self.DATA: self.data
        }, default=lambda o: o.to_json_str())

    @staticmethod
    def from_json_str(j: str) -> 'BoboEventSimple':
        return BoboEventSimple.from_dict(loads(j))

    @staticmethod
    def from_dict(d: dict) -> 'BoboEventSimple':
        return BoboEventSimple(
            event_id=d[BoboEventSimple.EVENT_ID],
            timestamp=d[BoboEventSimple.TIMESTAMP],
            data=d[BoboEventSimple.DATA]
        )

    def __str__(self) -> str:
        return self.to_json_str()
