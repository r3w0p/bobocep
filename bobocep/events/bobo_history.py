# Copyright (c) 2022 The BoboCEP Authors
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from typing import Dict, List, Union

from dpcontracts import require

from bobocep.events.bobo_event import BoboEvent


class BoboHistory:
    """A history of events.

    :param events: The history of events, where each key is a name for a list
                   of associated events.
    :type events: Dict[str, List[BoboEvent]]
    """

    @require("'events' must be of type dict",
             lambda args: isinstance(args.events,
                                     dict))
    @require("'events' keys must be of type str only",
             lambda args: all([isinstance(key, str)
                               for key in
                               args.events.keys()]))
    @require("'events' values must be of type list only",
             lambda args: all([isinstance(val, list)
                               for val in
                               args.events.values()]))
    @require("'events' lists must contain BoboEvent instances only",
             lambda args: all([
                 all(isinstance(val_str, BoboEvent)
                     for val_str in val_list)
                 for val_list in args.events.values()
             ]))
    def __init__(self, events: Dict[str, List[BoboEvent]]):
        super().__init__()

        self.events: Dict[str, List[BoboEvent]] = {}
        self.first: Union[BoboEvent, None] = None
        self.last: Union[BoboEvent, None] = None

        if events is not None:
            for name, event_list in events.items():
                for event in event_list:
                    if name not in self.events:
                        self.events[name] = []

                    self.events[name].append(event)

                    if self.first is None or \
                            event.timestamp < self.first.timestamp:
                        self.first = event

                    if self.last is None or \
                            event.timestamp > self.last.timestamp:
                        self.last = event
