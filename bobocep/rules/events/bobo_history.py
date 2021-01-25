from typing import Dict, List
from dpcontracts import require
from overrides import overrides
import sys

from bobocep.bobo_serializable import BoboSerializable
from bobocep.rules.bobo_rule import BoboRule
from bobocep.rules.events.bobo_event import BoboEvent


class BoboHistory(BoboSerializable, BoboRule):
    """A history of events.

    :param events: The history of events, where each key is a label with which
                    a list of events are associated.
    :type events: Dict[str, List[BoboEvent]]
    """

    HISTORY_EVENT = "history_event"
    HISTORY_EVENT_MODULE = "history_event_module"
    HISTORY_EVENT_CLASS = "history_event_class"

    @require("'history' must be a dict with keys of type str and values of "
             "lists of type BoboEvent",
             lambda args:
             isinstance(args.events, dict) and
             all([isinstance(key, str) for key in args.events.keys()]) and
             all([isinstance(val_list, list) and
                  all(isinstance(val_str, BoboEvent) for val_str in val_list)
                  for val_list in args.events.values()]))
    def __init__(self, events: Dict[str, List[BoboEvent]]) -> None:

        super().__init__()

        self.events = events
        self.first = None
        self.last = None

        for event_list in self.events.values():
            for event in event_list:
                if self.first is None or \
                        event.timestamp < self.first.timestamp:
                    self.first = event

                if self.last is None or \
                        event.timestamp > self.last.timestamp:
                    self.last = event

    @overrides
    def to_dict(self) -> dict:
        d = {}
        for key in self.events.keys():
            d[key] = []
            for event in self.events[key]:
                d[key].append({
                    self.HISTORY_EVENT: event.to_dict(),
                    self.HISTORY_EVENT_MODULE: event.__class__.__module__,
                    self.HISTORY_EVENT_CLASS: event.__class__.__name__
                })
        return d

    @staticmethod
    @overrides
    def from_dict(d: dict) -> 'BoboHistory':
        """
        :rtype: BoboHistory
        """
        events = {}
        for key in d.keys():
            events[key] = []
            for event_dict in d[key]:
                event_class = getattr(
                    sys.modules[event_dict[BoboHistory.HISTORY_EVENT_MODULE]],
                    event_dict[BoboHistory.HISTORY_EVENT_CLASS])
                events[key].append(
                    event_class.from_dict(
                        event_dict[BoboHistory.HISTORY_EVENT]))
        return BoboHistory(events=events)
