# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from datetime import datetime
from typing import Any

from bobocep.event.bobo_event import BoboEvent
from bobocep.event.bobo_history import BoboHistory


class BoboEventComplex(BoboEvent):
    """A complex event.

    :param pattern_name: The pattern which generated the event.
    :type pattern_name: str

    :param history: The history of events associated with the event.
    :type history: BoboHistory
    """

    def __init__(self,
                 event_id: str,
                 timestamp: datetime,
                 data: Any,
                 process_name: str,
                 pattern_name: str,
                 history: BoboHistory):
        super().__init__(
            event_id=event_id,
            timestamp=timestamp,
            data=data)

        if len(process_name) == 0:
            pass  # todo raise exception

        if len(pattern_name) == 0:
            pass  # todo raise exception

        self.process_name = process_name
        self.pattern_name = pattern_name
        self.history = history
