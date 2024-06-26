# Copyright (c) 2019-2024 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Abstract event.
"""

from abc import ABC, abstractmethod
from typing import Any

from bobocep import BoboError, BoboJSONable

_EXC_ID_LEN = "event ID must have a length greater than 0"


class BoboEventError(BoboError):
    """
    An event error.
    """


class BoboEvent(BoboJSONable, ABC):
    """
    An abstract event.
    """

    EVENT_TYPE = "event_type"
    EVENT_ID = "event_id"
    TIMESTAMP = "timestamp"
    DATA = "data"

    def __init__(self,
                 event_id: str,
                 timestamp: int,
                 data: Any):
        """
        :param event_id: The event ID.
        :param timestamp: The event timestamp.
        :param data: The event data.

        :raises BoboEventError: If length of event ID is equal to 0.
        """
        super().__init__()

        if len(event_id) == 0:
            raise BoboEventError(_EXC_ID_LEN)

        self._event_id: str = event_id
        self._timestamp: int = timestamp
        self._data: Any = data

    @abstractmethod
    def cast(self, dtype: type) -> 'BoboEvent':
        """
        :param dtype: The type to which the event's data is cast.
        :return: A new BoboEvent instance with its data cast to `dtype`
            and all other properties identical to the original event.
        """

    @property
    def event_id(self) -> str:
        """
        Get event ID.
        """
        return self._event_id

    @property
    def timestamp(self) -> int:
        """
        Get event timestamp.
        """
        return self._timestamp

    @property
    def data(self) -> Any:
        """
        Get event data.
        """
        return self._data
