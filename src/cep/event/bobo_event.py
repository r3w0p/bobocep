# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from abc import ABC, abstractmethod
from typing import Any

from src.cep.event.bobo_event_error import BoboEventError
from src.misc.bobo_jsonable import BoboJSONable


class BoboEvent(BoboJSONable, ABC):
    """An event."""

    EVENT_TYPE = "event_type"
    EVENT_ID = "event_id"
    TIMESTAMP = "timestamp"
    DATA = "data"

    _EXC_ID_LEN = "'event_id_gen' must have a length greater than 0"

    def __init__(self,
                 event_id: str,
                 timestamp: int,
                 data: Any):
        super().__init__()

        # TODO Note: timestamp = milliseconds from epoch is the point where
        #  the time starts, the return value of time.gmtime(0). It is
        #  January 1, 1970, 00:00:00 (UTC) on all platforms.

        if len(event_id) == 0:
            raise BoboEventError(self._EXC_ID_LEN)

        self._event_id: str = event_id
        self._timestamp: int = timestamp
        self._data: Any = data

    @staticmethod
    @abstractmethod
    def from_dict(d: dict) -> 'BoboEvent':
        """"""

    @property
    def event_id(self) -> str:
        return self._event_id

    @property
    def timestamp(self) -> int:
        return self._timestamp

    @property
    def data(self):
        return self._data