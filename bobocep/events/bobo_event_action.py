from datetime import datetime

from bobocep.events.bobo_event import BoboEvent


class BoboEventAction(BoboEvent):
    """An action event."""

    def __init__(self,
                 event_id: str,
                 timestamp: datetime,
                 data):
        super().__init__(
            event_id=event_id,
            timestamp=timestamp,
            data=data)
