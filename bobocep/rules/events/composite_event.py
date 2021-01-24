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

    :param nfa_key: The NFA key associated with the composite event.
    :type nfa_key: str

    :param history: The history of events associated with the composite event.
    :type history: Dict[str, List[BoboEvent]]
    """

    EVENT_NAME = "event_name"
    NFA_KEY = "nfa_key"
    HISTORY = "history"
    HISTORY_EVENT = "history_event"
    HISTORY_EVENT_CLASS = "history_event_class"

    @require("'name' must be a str",
             lambda args: isinstance(args.event_name, str))
    @require("'nfa_key' must be a str",
             lambda args: isinstance(args.nfa_key, str))
    @require("'events' must be a dict with keys of type str and values of "
             "lists of type BoboEvent",
             lambda args:
             isinstance(args.events, dict) and
             all([isinstance(key, str) for key in args.events.keys()]) and
             all([isinstance(val_list, list) and
                  all(isinstance(val_str, BoboEvent) for val_str in val_list)
                  for val_list in args.events.values()]))
    def __init__(self,
                 event_id: str,
                 timestamp: int,
                 data: Dict[str, str],
                 event_name: str,
                 nfa_key: str,
                 history: Dict[str, List[BoboEvent]]) -> None:

        super().__init__(event_id=event_id,
                         timestamp=timestamp,
                         data=data)

        self.event_name = event_name
        self.nfa_key = nfa_key
        self.history = history

        self.history_first = None
        self.history_last = None

        for event_list in self.history.values():
            for event in event_list:
                if self.first is None or \
                        event.timestamp < self.first.timestamp:
                    self.first = event

                if self.last is None or event.timestamp > self.last.timestamp:
                    self.last = event

    @overrides
    def to_dict(self) -> dict:
        d = {
            self.EVENT_ID: self.event_id,
            self.TIMESTAMP: self.timestamp,
            self.DATA: self.data,
            self.EVENT_NAME: self.event_name,
            self.NFA_KEY: self.nfa_key,
        }

        history_dict = {}
        for key in self.history.keys():
            for event in self.history[key]:
                history_dict[key] = {
                    self.HISTORY_EVENT: event.to_dict(),
                    self.HISTORY_EVENT_CLASS: event.__class__
                }
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
            nfa_key=d[self.NFA_KEY],
            history=history
        )
