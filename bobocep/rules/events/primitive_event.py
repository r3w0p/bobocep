from typing import Dict
from overrides import overrides

from bobocep.rules.events.bobo_event import BoboEvent


class PrimitiveEvent(BoboEvent):
    """A primitive event.

    :param event_id: The event ID.
    :type event_id: str

    :param timestamp: The timestamp indicating when the event was recorded.
    :type timestamp: int

    :param data: The event data.
    :type data: Dict[str, str]
    """

    def __init__(self,
                 event_id: str,
                 timestamp: int,
                 data: Dict[str, str]) -> None:
        super().__init__(event_id=event_id,
                         timestamp=timestamp,
                         data=data)

    @overrides
    def to_dict(self) -> dict:
        return {
            self.EVENT_ID: self.event_id,
            self.TIMESTAMP: self.timestamp,
            self.DATA: self.data
        }

    @staticmethod
    @overrides
    def from_dict(d: dict) -> 'PrimitiveEvent':
        return PrimitiveEvent(
            event_id=d[PrimitiveEvent.EVENT_ID],
            timestamp=d[PrimitiveEvent.TIMESTAMP],
            data=d[PrimitiveEvent.DATA]
        )
