from bobocep.rules.events.bobo_event import BoboEvent
from typing import Dict, List
from dpcontracts import require
from overrides import overrides


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

    :param nfa_id: The NFA key associated with the composite event.
    :type nfa_id: str

    :param history: The history of events associated with the composite event.
    :type history: Dict[str, List[BoboEvent]]
    """

    EVENT_NAME = "event_name"
    NFA_ID = "nfa_id"
    HISTORY = "history"
    HISTORY_EVENT = "history_event"
    HISTORY_EVENT_CLASS = "history_event_class"

    @require("'name' must be a str",
             lambda args: isinstance(args.event_name, str))
    @require("'nfa_id' must be a str",
             lambda args: isinstance(args.nfa_id, str))
    @require("'history' must be a dict with keys of type str and values of "
             "lists of type BoboEvent",
             lambda args:
             isinstance(args.history, dict) and
             all([isinstance(key, str) for key in args.history.keys()]) and
             all([isinstance(val_list, list) and
                  all(isinstance(val_str, BoboEvent) for val_str in val_list)
                  for val_list in args.history.values()]))
    def __init__(self,
                 event_id: str,
                 timestamp: int,
                 data: Dict[str, str],
                 event_name: str,
                 nfa_id: str,
                 history: Dict[str, List[BoboEvent]]) -> None:

        super().__init__(event_id=event_id,
                         timestamp=timestamp,
                         data=data)

        self.event_name = event_name
        self.nfa_id = nfa_id
        self.history = history

        self.history_first = None
        self.history_last = None

        for event_list in self.history.values():
            for event in event_list:
                if self.history_first is None or \
                        event.timestamp < self.history_first.timestamp:
                    self.history_first = event

                if self.history_last is None or \
                        event.timestamp > self.history_last.timestamp:
                    self.history_last = event

    @overrides
    def to_dict(self) -> dict:
        d = {
            self.EVENT_ID: self.event_id,
            self.TIMESTAMP: self.timestamp,
            self.DATA: self.data,
            self.EVENT_NAME: self.event_name,
            self.NFA_ID: self.nfa_id,
        }

        history_dict = {}
        for key in self.history.keys():
            history_dict[key] = []
            for event in self.history[key]:
                history_dict[key].append({
                    self.HISTORY_EVENT: event.to_dict(),
                    self.HISTORY_EVENT_CLASS: event.__class__.__name__
                })
        d[self.HISTORY] = history_dict

        return d

    @overrides
    def from_dict(self, d: dict) -> 'CompositeEvent':
        history = {}
        for key in d[self.HISTORY].keys():
            history[key] = []
            for event_dict in d[self.HISTORY][key]:
                event_class = globals()[event_dict[self.HISTORY_EVENT_CLASS]]
                history[key].append(
                    event_class.from_dict(event_dict[self.HISTORY_EVENT]))

        return CompositeEvent(
            event_id=d[self.EVENT_ID],
            timestamp=d[self.TIMESTAMP],
            data=d[self.DATA],
            event_name=d[self.EVENT_NAME],
            nfa_id=d[self.NFA_ID],
            history=history
        )
