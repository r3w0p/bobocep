from typing import Dict

from dpcontracts import require

from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.bobo_history import BoboHistory


class CompositeEvent(BoboEvent):
    """A composite event.

    :param event_id: The event ID.
    :type event_id: str

    :param timestamp: The timestamp indicating when the event was recorded.
    :type timestamp: int

    :param data: The event data.
    :type data: Dict[str, str]

    :param event_name: The composite event name.
    :type event_name: str

    :param nfa_name: The NFA name associated with the composite event.
    :type nfa_name: str

    :param history: The history of events associated with the composite event.
    :type history: BoboHistory
    """

    @require("'name' must be a str",
             lambda args: isinstance(args.event_name, str))
    @require("'nfa_name' must be a str",
             lambda args: isinstance(args.nfa_name, str))
    @require("'history' must be an instance of BoboHistory",
             lambda args: isinstance(args.history, BoboHistory))
    def __init__(self,
                 event_id: str,
                 timestamp: int,
                 data: Dict[str, str],
                 event_name: str,
                 nfa_name: str,
                 history: BoboHistory):
        super().__init__(event_id=event_id, timestamp=timestamp, data=data)

        self.event_name = event_name
        self.nfa_name = nfa_name
        self.history = history
