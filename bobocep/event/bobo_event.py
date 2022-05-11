# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from abc import ABC

from datetime import datetime
from typing import Any


class BoboEvent(ABC):
    """An event.

    :param event_id: The event ID.
    :type event_id: str

    :param timestamp: The event timestamp.
    :type timestamp: datetime

    :param data: The event data.
    :type data: Any
    """

    def __init__(self,
                 event_id: str,
                 timestamp: datetime,
                 data: Any):
        super().__init__()

        self.event_id = event_id
        self.timestamp = timestamp
        self.data = data
