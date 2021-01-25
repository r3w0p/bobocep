from typing import Dict
from copy import copy
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

    :param nfa_name: The NFA name associated with the composite event.
    :type nfa_name: str

    :param history: The history of events associated with the composite event.
    :type history: BoboHistory
    """

    EVENT_NAME = "event_name"
    NFA_NAME = "nfa_name"
    HISTORY = "history"

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
                 history: BoboHistory) -> None:

        super().__init__(event_id=event_id,
                         timestamp=timestamp,
                         data=data)

        self.event_name = event_name
        self.nfa_name = nfa_name
        self.history = history

    @overrides
    def to_dict(self) -> dict:
        return {
            self.EVENT_ID: self.event_id,
            self.TIMESTAMP: self.timestamp,
            self.DATA: copy(self.data),
            self.EVENT_NAME: self.event_name,
            self.NFA_NAME: self.nfa_name,
            self.HISTORY: self.history.to_dict()
        }

    @staticmethod
    @overrides
    def from_dict(d: dict) -> 'CompositeEvent':
        """
        :rtype: CompositeEvent
        """
        return CompositeEvent(
            event_id=d[CompositeEvent.EVENT_ID],
            timestamp=d[CompositeEvent.TIMESTAMP],
            data=d[CompositeEvent.DATA],
            event_name=d[CompositeEvent.EVENT_NAME],
            nfa_name=d[CompositeEvent.NFA_NAME],
            history=BoboHistory.from_dict(d[CompositeEvent.HISTORY])
        )
