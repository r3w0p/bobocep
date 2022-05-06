# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from typing import Dict, List, Union

from bobocep.event.bobo_event import BoboEvent


class BoboHistory:
    """A history of events.

    :param events: The history of events, where each key is a name for a list
                   of associated events.
    :type events: Dict[str, List[BoboEvent]]
    """

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
