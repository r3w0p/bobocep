# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from json import dumps, loads
from typing import Dict, List, Tuple, Optional

from src.cep.event.bobo_event import BoboEvent
from src.misc.bobo_jsonable import BoboJSONable


class BoboHistory(BoboJSONable):
    """An event history."""

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

    def to_json_str(self) -> str:
        d: Dict[str, List[BoboEvent]] = {}

        for key in self._events:
            d[key] = [e for e in self._events[key]]

        return dumps(d, default=lambda o: o.to_json_str())

    @staticmethod
    def from_json_str(j: str) -> 'BoboHistory':
        return BoboHistory.from_dict(loads(j))

    @staticmethod
    def from_dict(d: dict) -> 'BoboHistory':
        from src.cep.event.bobo_event_factory import BoboEventFactory

        events: Dict[str, List[BoboEvent]] = {}

        for key in d:
            events[key] = [BoboEventFactory.from_json_str(e) for e in d[key]]

        return BoboHistory(events=events)
