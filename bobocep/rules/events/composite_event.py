from typing import Dict
from dpcontracts import require
from overrides import overrides

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

    :param nfa_id: The NFA ID associated with the composite event.
    :type nfa_id: str

    :param history: The history of events associated with the composite event.
    :type history: BoboHistory
    """

    EVENT_NAME = "event_name"
    NFA_ID = "nfa_id"
    HISTORY = "history"

    @require("'name' must be a str",
             lambda args: isinstance(args.event_name, str))
    @require("'nfa_id' must be a str",
             lambda args: isinstance(args.nfa_id, str))
    @require("'history' must be an instance of BoboHistory",
             lambda args: isinstance(args.history, BoboHistory))
    def __init__(self,
                 event_id: str,
                 timestamp: int,
                 data: Dict[str, str],
                 event_name: str,
                 nfa_id: str,
                 history: BoboHistory) -> None:

        super().__init__(event_id=event_id,
                         timestamp=timestamp,
                         data=data)

        self.event_name = event_name
        self.nfa_id = nfa_id
        self.history = history

    @overrides
    def to_dict(self) -> dict:
        return {
            self.EVENT_ID: self.event_id,
            self.TIMESTAMP: self.timestamp,
            self.DATA: self.data,
            self.EVENT_NAME: self.event_name,
            self.NFA_ID: self.nfa_id,
            self.HISTORY: self.history.to_dict()
        }

    @staticmethod
    @overrides
    def from_dict(d: dict) -> 'CompositeEvent':
        return CompositeEvent(
            event_id=d[CompositeEvent.EVENT_ID],
            timestamp=d[CompositeEvent.TIMESTAMP],
            data=d[CompositeEvent.DATA],
            event_name=d[CompositeEvent.EVENT_NAME],
            nfa_id=d[CompositeEvent.NFA_ID],
            history=BoboHistory.from_dict(d[CompositeEvent.HISTORY])
        )
