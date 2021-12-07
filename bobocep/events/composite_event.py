from typing import Dict

from dpcontracts import require

from bobocep.events.bobo_event import BoboEvent
from bobocep.events.bobo_history import BoboHistory


class CompositeEvent(BoboEvent):
    """A composite event.

    :param event_name: The composite event name.
    :type event_name: str

    :param pattern_name: The pattern which generated the composite event.
    :type pattern_name: str

    :param history: The history of events associated with the composite event.
    :type history: BoboHistory
    """

    @require("'event_name' must be of type str",
             lambda args: isinstance(args.event_name, str))
    @require("'pattern_name' must be of type str",
             lambda args: isinstance(args.pattern_name, str))
    @require("'history' must be an instance of BoboHistory",
             lambda args: isinstance(args.history, BoboHistory))
    def __init__(self,
                 event_id: str,
                 timestamp: int,
                 data_type: type,
                 data,
                 event_name: str,
                 pattern_name: str,
                 history: BoboHistory):
        super().__init__(
            event_id=event_id,
            timestamp=timestamp,
            data_type=data_type,
            data=data)

        self.event_name = event_name
        self.pattern_name = pattern_name
        self.history = history
