# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from typing import Any

from src.cep.event.bobo_event import BoboEvent


class BoboEventSimple(BoboEvent):
    """A simple event."""

    def __init__(self,
                 event_id: str,
                 timestamp: int,
                 data: Any):
        super().__init__(
            event_id=event_id,
            timestamp=timestamp,
            data=data)

    def to_dict(self) -> dict:
        return {
            self.EVENT_TYPE: self.__class__.__name__,
            self.EVENT_ID: self.event_id,
            self.TIMESTAMP: self.timestamp,
            self.DATA: self.data,
            self.DATA_TYPE: type(self.data).__name__
        }

    @staticmethod
    def from_dict(d: dict) -> 'BoboEventSimple':
        BoboEventSimple.validate_dict(d, [
            (BoboEventSimple.EVENT_ID, str),
            (BoboEventSimple.TIMESTAMP, int),
            (BoboEventSimple.DATA, None),
            (BoboEventSimple.DATA_TYPE, str),
        ])

        t = getattr(__builtins__, d[BoboEventSimple.DATA_TYPE])

        return BoboEventSimple(
            event_id=d[BoboEventSimple.EVENT_ID],
            timestamp=d[BoboEventSimple.TIMESTAMP],
            data=t(d[BoboEventSimple.DATA])
        )
