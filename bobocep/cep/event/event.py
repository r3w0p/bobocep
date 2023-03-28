# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from abc import ABC, abstractmethod
from typing import Any

from bobocep import BoboError
from bobocep.cep.event.constants import *
from bobocep.cep.json import BoboJSONable


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
            raise BoboEventError(EXC_ID_LEN)

        self._event_id: str = event_id
        self._timestamp: int = timestamp
        self._data: Any = data

    @abstractmethod
    def cast(self, dtype: type) -> 'BoboEvent':
        """
        :param dtype: The type to which the data is cast.
        :return: A new instance of the BoboEvent with its data cast to `dtype`
            and all other properties identical to the original BoboEvent.
        """

    @staticmethod
    @abstractmethod
    def from_dict(d: dict) -> 'BoboEvent':
        """
        :param d: A BoboEvent in `dict` format.
        :return: A BoboEvent instance with the properties defined in `d`.
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
