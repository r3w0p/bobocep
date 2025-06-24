# Copyright (c) 2019-2024 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Event history.
"""

from json import dumps, loads
from typing import Dict, List, Optional

from bobocep.bobocep import BoboJSONable
from bobocep.cep.event.event import BoboEvent


class BoboHistory(BoboJSONable):
    """
    An event history.
    """

    __slots__ = ("_events", "_first", "_last")
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
            for group, event_list in events.items():
                for event in event_list:
                    if group not in self._events:
                        self._events[group] = []

                    self._events[group].append(event)

                    if self._first is None or \
                            event.timestamp < self._first.timestamp:
                        self._first = event

                    if self._last is None or \
                            event.timestamp > self._last.timestamp:
                        self._last = event

    def events(self, group: str) -> List[BoboEvent]:
        """
        :param group: A group name.
        :return: The history events associated with `group`.
        """
        if group in self._events:
            return [*self._events[group]]
        else:
            return []

    @property
    def all_events(self) -> List[BoboEvent]:
        """
        :return: All events in the history.
        """
        all_events = []

        for group in self._events:
            all_events += self._events[group]

        return all_events

    @property
    def all_groups(self) -> List[str]:
        """
        :return: All groups in the history.
        """
        return [*self._events]

    @property
    def first(self) -> Optional[BoboEvent]:
        """
        :return: The BoboEvent with the oldest timestamp.
        """
        return self._first

    @property
    def last(self) -> Optional[BoboEvent]:
        """
        :return: The BoboEvent with the most recent timestamp.
        """
        return self._last

    def add(self, group: str, event: BoboEvent) -> 'BoboHistory':
        """
        :param group: A group name.
        :param event: The event to add.

        :return: A new BoboHistory instance with `event` in `group`.
        """
        new_events: Dict[str, List[BoboEvent]] = {}

        # Copy events from existing history
        for g in self._events:
            new_events[g] = [*self._events[g]]

        # Add in new event (and group if new)
        if group not in new_events:
            new_events[group] = []

        new_events[group].append(event)

        # Create new history
        return BoboHistory(events=new_events)

    def size(self) -> int:
        """
        :return: The total number of history events across all groups.
        """
        count = 0

        for group in self._events:
            count += len(self._events[group])

        return count

    def to_json_dict(self) -> dict:
        """
        :return: A JSON `dict` representation of the history.
        """
        d: Dict[str, List[BoboEvent]] = {}

        for group in self._events:
            d[group] = [*self._events[group]]

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
