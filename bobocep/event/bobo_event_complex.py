# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from datetime import datetime

from bobocep.event.bobo_event import BoboEvent
from bobocep.event.bobo_history import BoboHistory


class BoboEventComplex(BoboEvent):
    """A complex event.

    :param pattern_name: The pattern which generated the composite event.
    :type pattern_name: str

    :param history: The history of event associated with the composite event.
    :type history: BoboHistory
    """

    def __init__(self,
                 event_id: str,
                 timestamp: datetime,
                 data,
                 process_name: str,
                 pattern_name: str,
                 history: BoboHistory):
        super().__init__(
            event_id=event_id,
            timestamp=timestamp,
            data=data)

        self.process_name = process_name
        self.pattern_name = pattern_name
        self.history = history
