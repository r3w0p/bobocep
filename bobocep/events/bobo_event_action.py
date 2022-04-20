# Copyright (c) The BoboCEP Authors
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License v3.0.

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
