from typing import Dict

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
