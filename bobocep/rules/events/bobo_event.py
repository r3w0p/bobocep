from bobocep.rules.bobo_rule import BoboRule
from abc import ABC
from typing import Dict
from dpcontracts import require


class BoboEvent(BoboRule, ABC):
    """A :code:`bobocep` event.

    :param event_id: The event ID.
    :type event_id: str

    :param timestamp: The timestamp indicating when the event was recorded.
    :type timestamp: int

    :param data: The event data.
    :type data: Dict[str, str]
    """

    EVENT_ID = "event_id"
    TIMESTAMP = "timestamp"
    DATA = "data"

    @require("'event_id' must be a str",
             lambda args: isinstance(args.event_id, str))
    @require("'timestamp' must be an int",
             lambda args: isinstance(args.timestamp, int))
    @require("'data' must be a dict with keys and values of only type str",
             lambda args:
             isinstance(args.data, dict) and
             all([isinstance(key, str) for key in args.data.keys()]) and
             all([isinstance(val, str) for val in args.data.values()]))
    def __init__(self,
                 event_id: str,
                 timestamp: int,
                 data: Dict[str, str]) -> None:
        super().__init__()

        self.event_id = event_id
        self.timestamp = timestamp
        self.data = data
