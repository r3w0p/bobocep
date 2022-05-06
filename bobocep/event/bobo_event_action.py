# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from datetime import datetime

from bobocep.event.bobo_event import BoboEvent


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

        # todo action event implementation
