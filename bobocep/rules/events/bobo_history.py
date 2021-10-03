from typing import Dict, List

from dpcontracts import require

from bobocep.rules.bobo_rule import BoboRule
from bobocep.rules.events.bobo_event import BoboEvent


class BoboHistory(BoboRule):
    """A history of events.

    :param events: The history of events, where each key is a group with which
                   a list of events are associated.
    :type events: Dict[str, List[BoboEvent]]
    """

    @require("'history' must be a dict with keys of type str and values of "
             "lists of type BoboEvent",
             lambda args:
             isinstance(args.events, dict) and
             all([isinstance(key, str) for key in args.events.keys()]) and
             all([isinstance(val_list, list) and
                  all(isinstance(val_str, BoboEvent) for val_str in val_list)
                  for val_list in args.events.values()]))
    def __init__(self, events: Dict[str, List[BoboEvent]]):

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
