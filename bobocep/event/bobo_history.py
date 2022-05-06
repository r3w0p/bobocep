# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from typing import Dict, List, Union, Tuple

from bobocep.event.bobo_event import BoboEvent


class BoboHistory:
    """A history of events.

    :param events: A history of events, where the key is a group name for a
                   list of associated events.
    :type events: Dict[str, List[BoboEvent]]
    """

    def __init__(self, events: Dict[str, List[BoboEvent]]):
        super().__init__()

        self._events: Dict[str, List[BoboEvent]] = {}
        self._first: Union[BoboEvent, None] = None
        self._last: Union[BoboEvent, None] = None

        if events is not None:
            for name, event_list in events.items():
                for event in event_list:
                    if name not in self._events:
                        self._events[name] = []

                    self._events[name].append(event)

                    if self._first is None or \
                            event.timestamp < self._first.timestamp:
                        self._first = event

                    if self._last is None or \
                            event.timestamp > self._last.timestamp:
                        self._last = event

    def all(self) -> Tuple[BoboEvent, ...]:
        all_events = []
        for key in self._events:
            all_events += self._events[key]
        return tuple(all_events)

    def group(self, group: str) -> Tuple[BoboEvent, ...]:
        if group in self._events:
            return tuple(self._events[group])
        else:
            return tuple()

    def first(self) -> Union[BoboEvent, None]:
        return self._first

    def last(self) -> Union[BoboEvent, None]:
        return self._last
