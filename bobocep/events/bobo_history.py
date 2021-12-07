from typing import Dict, List

from dpcontracts import require

from bobocep.events.bobo_event import BoboEvent


class BoboHistory:
    """A history of events.

    :param events: The history of events, where each key is a group with a
                   list of associated events as its value.
    :type events: Dict[str, List[BoboEvent]]
    """

    @require("'history' must be of type dict",
             lambda args: isinstance(args.events, dict))
    @require("'history' keys must be of type str only",
             lambda args: all([isinstance(key, str)
                               for key in args.events.keys()]))
    @require("'history' values must be of type list only",
             lambda args: all([isinstance(val, list)
                               for val in args.events.values()]))
    @require("'history' value lists must contain BoboEvent instances only",
             lambda args: all([
                 all(isinstance(val_str, BoboEvent)
                     for val_str in val_list)
                 for val_list in args.events.values()
             ]))
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
