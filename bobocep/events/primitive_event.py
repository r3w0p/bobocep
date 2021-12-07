from bobocep.events.bobo_event import BoboEvent


class PrimitiveEvent(BoboEvent):
    """A primitive event."""

    def __init__(self,
                 event_id: str,
                 timestamp: int,
                 data_type: type,
                 data):
        super().__init__(
            event_id=event_id,
            timestamp=timestamp,
            data_type=data_type,
            data=data)
