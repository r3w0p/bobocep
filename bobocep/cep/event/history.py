# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Event history.
"""

from json import dumps, loads
from typing import Dict, List, Optional, Tuple

from bobocep.bobocep import BoboJSONable
from bobocep.cep.event.event import BoboEvent


class BoboHistory(BoboJSONable):
    """
    An event history.
    """

    def __init__(self, events: Dict[str, List[BoboEvent]]):
        """
        :param events: The history of events.
            Keys are group names.
            Values are lists of BoboEvent instances associated with a group.
        """
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

    @property
    def events(self) -> Dict[str, List[BoboEvent]]:
        """
        :return: All history events, indexed by group.
        """
        eventscopy: Dict[str, List[BoboEvent]] = {}

        for grp in self._events.keys():
            if grp not in eventscopy:
                eventscopy[grp] = []

            eventscopy[grp] = [eve for eve in self._events[grp]]

        return eventscopy

    def size(self) -> int:
        """
        :return: The total number of history events across all groups.
        """
        count = 0

        for grp in self._events.keys():
            count += len(self._events[grp])

        return count

    def all_groups(self) -> Tuple[str, ...]:
        """
        :return: All history groups in a tuple.
        """
        return tuple(self._events.keys())

    def all_events(self) -> Tuple[BoboEvent, ...]:
        """
        :return: All history events in a tuple.
        """
        all_events = []
        for grp in self._events.keys():
            all_events += self._events[grp]
        return tuple(all_events)

    def group(self, group: str) -> Tuple[BoboEvent, ...]:
        """
        :param group: A group name.
        :return: The BoboEvent instances associated with `group`.
        """
        if group in self._events:
            return tuple(self._events[group])
        else:
            return tuple()

    def first(self) -> Optional[BoboEvent]:
        """
        :return: The BoboEvent with the oldest timestamp,
            if there is at least one BoboEvent in the history.
        """
        return self._first

    def last(self) -> Optional[BoboEvent]:
        """
        :return: The BoboEvent with the most recent timestamp,
            if there is at least one BoboEvent in the history.
        """
        return self._last

    def to_json_dict(self) -> dict:
        """
        :return: A JSON `dict` representation of the history.
        """
        d: Dict[str, List[BoboEvent]] = {}

        for key in self._events:
            d[key] = [e for e in self._events[key]]

        return d

    def to_json_str(self) -> str:
        """
        :return: A JSON `str` representation of the history.
        """
        return dumps(self.to_json_dict(), default=lambda o: o.to_json_str())

    @staticmethod
    def from_json_str(j: str) -> 'BoboHistory':
        """
        :param j: A JSON `str` representation of the history.
        :return: A new instance of the history.
        """
        return BoboHistory.from_json_dict(loads(j))

    @staticmethod
    def from_json_dict(d: dict) -> 'BoboHistory':
        """
        :param d: A JSON `dict` representation of the history.
        :return: A new instance of the history.
        """
        from bobocep.cep.event.factory import BoboEventFactory

        events: Dict[str, List[BoboEvent]] = {}

        for key in d:
            events[key] = [BoboEventFactory.from_json_str(e) for e in d[key]]

        return BoboHistory(events=events)

    def __str__(self) -> str:
        """
        :return: A JSON `str` representation of the history.
        """
        return self.to_json_str()
