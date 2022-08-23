# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from json import dumps
from typing import Dict, List, Tuple, Optional

from bobocep.event.bobo_event import BoboEvent


class BoboHistory:
    """A history of events."""

    def __init__(self, events: Dict[str, List[BoboEvent]]):
        super().__init__()

        self._events: Dict[str, List[BoboEvent]] = {}
        self._first: Optional[BoboEvent] = None
        self._last: Optional[BoboEvent] = None

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

    def first(self) -> Optional[BoboEvent]:
        return self._first

    def last(self) -> Optional[BoboEvent]:
        return self._last

    def __str__(self) -> str:
        e: Dict[str, List[str]] = {}

        for name, event_list in self._events.items():
            for event in event_list:
                if name not in e:
                    e[name] = []

                e[name].append(event.event_id)

        return dumps(e)
