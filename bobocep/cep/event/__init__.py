# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Event types.
"""

from abc import ABC, abstractmethod
from json import dumps, loads
from typing import Any, Tuple, Optional, Dict, List

from bobocep import BoboError
from bobocep.cep import BoboJSONable


class BoboEventError(BoboError):
    """
    An event error.
    """


class BoboEventFactoryError(BoboEventError):
    """
    An event factory error.
    """


class BoboEvent(BoboJSONable, ABC):
    """
    An abstract event.
    """

    EVENT_TYPE = "event_type"
    EVENT_ID = "event_id"
    TIMESTAMP = "timestamp"
    DATA = "data"

    _EXC_ID_LEN = "'event_id' must have a length greater than 0"

    def __init__(self,
                 event_id: str,
                 timestamp: int,
                 data: Any):
        """
        :param event_id: The event ID.
        :param timestamp: The event timestamp.
        :param data: The event data.

        :raises BoboEventError: If length of event ID is equal to 0.
        """
        super().__init__()

        if len(event_id) == 0:
            raise BoboEventError(self._EXC_ID_LEN)

        self._event_id: str = event_id
        self._timestamp: int = timestamp
        self._data: Any = data

    @abstractmethod
    def cast(self, dtype: type) -> 'BoboEvent':
        """
        :param dtype: The type to which the data is cast.
        :return: A new instance of the BoboEvent with its data cast to `dtype`
            and all other properties identical to the original BoboEvent.
        """

    @staticmethod
    @abstractmethod
    def from_dict(d: dict) -> 'BoboEvent':
        """
        :param d: A BoboEvent in `dict` format.
        :return: A BoboEvent instance with the properties defined in `d`.
        """

    @property
    def event_id(self) -> str:
        """
        Get event ID.
        """
        return self._event_id

    @property
    def timestamp(self) -> int:
        """
        Get event timestamp.
        """
        return self._timestamp

    @property
    def data(self) -> Any:
        """
        Get event data.
        """
        return self._data


class BoboEventAction(BoboEvent):
    """
    An action event.
    """

    TYPE_ACTION = "action"

    PHENOMENON_NAME = "phenomenon_name"
    PATTERN_NAME = "pattern_name"
    ACTION_NAME = "action_name"
    SUCCESS = "success"

    _EXC_PRO_LEN = "phenomenon name must have a length greater than 0"
    _EXC_PAT_LEN = "pattern name must have a length greater than 0"
    _EXC_ACT_LEN = "action name must have a length greater than 0"

    def __init__(self,
                 event_id,
                 timestamp: int,
                 data: Any,
                 phenomenon_name: str,
                 pattern_name: str,
                 action_name: str,
                 success: bool):
        """
        :param event_id: The event ID.
        :param timestamp: The event timestamp.
        :param data: The event data.
        :param phenomenon_name: The phenomenon name.
        :param pattern_name: The pattern name.
        :param action_name: The action name.
        :param success: `True` if the action was successful;
            `False` otherwise.

        :raises BoboEventError: If length of phenomenon name is equal to 0.
        :raises BoboEventError: If length of pattern name is equal to 0.
        :raises BoboEventError: If length of action name is equal to 0.
        """
        super().__init__(
            event_id=event_id,
            timestamp=timestamp,
            data=data)

        if len(phenomenon_name) == 0:
            raise BoboEventError(self._EXC_PRO_LEN)

        if len(pattern_name) == 0:
            raise BoboEventError(self._EXC_PAT_LEN)

        if len(action_name) == 0:
            raise BoboEventError(self._EXC_ACT_LEN)

        self._phenomenon_name: str = phenomenon_name
        self._pattern_name: str = pattern_name
        self._action_name: str = action_name
        self._success: bool = success

    def cast(self, dtype: type) -> 'BoboEventAction':
        return BoboEventAction(
            event_id=self._event_id,
            timestamp=self._timestamp,
            data=dtype(self._data),
            phenomenon_name=self._phenomenon_name,
            pattern_name=self._pattern_name,
            action_name=self._action_name,
            success=self._success
        )

    @property
    def phenomenon_name(self) -> str:
        """
        Get phenomenon name.
        """
        return self._phenomenon_name

    @property
    def pattern_name(self) -> str:
        """
        Get pattern name.
        """
        return self._pattern_name

    @property
    def action_name(self) -> str:
        """
        Get action name.
        """
        return self._action_name

    @property
    def success(self) -> bool:
        """
        Get success.
        """
        return self._success

    def to_json_str(self) -> str:
        return dumps({
            self.EVENT_TYPE: self.TYPE_ACTION,
            self.EVENT_ID: self.event_id,
            self.TIMESTAMP: self.timestamp,
            self.DATA: self.data,
            self.PHENOMENON_NAME: self.phenomenon_name,
            self.PATTERN_NAME: self.pattern_name,
            self.ACTION_NAME: self.action_name,
            self.SUCCESS: self.success
        }, default=lambda o: o.to_json_str())

    @staticmethod
    def from_json_str(j: str) -> 'BoboEventAction':
        return BoboEventAction.from_dict(loads(j))

    @staticmethod
    def from_dict(d: dict) -> 'BoboEventAction':
        return BoboEventAction(
            event_id=d[BoboEventAction.EVENT_ID],
            timestamp=d[BoboEventAction.TIMESTAMP],
            data=d[BoboEventAction.DATA],
            phenomenon_name=d[BoboEventAction.PHENOMENON_NAME],
            pattern_name=d[BoboEventAction.PATTERN_NAME],
            action_name=d[BoboEventAction.ACTION_NAME],
            success=d[BoboEventAction.SUCCESS]
        )

    def __str__(self) -> str:
        return self.to_json_str()


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

    def all(self) -> Tuple[BoboEvent, ...]:
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
        events: Dict[str, List[BoboEvent]] = {}

        for key in d:
            events[key] = [BoboEventFactory.from_json_str(e) for e in d[key]]

        return BoboHistory(events=events)

    def __str__(self) -> str:
        return self.to_json_str()


class BoboEventComplex(BoboEvent):
    """
    A complex event.
    """

    TYPE_COMPLEX = "complex"

    PHENOMENON_NAME = "phenomenon_name"
    PATTERN_NAME = "pattern_name"
    HISTORY = "history"

    _EXC_PRO_LEN = "phenomenon name must have a length greater than 0"
    _EXC_PAT_LEN = "pattern name must have a length greater than 0"

    def __init__(self,
                 event_id: str,
                 timestamp: int,
                 data: Any,
                 phenomenon_name: str,
                 pattern_name: str,
                 history: BoboHistory):
        """
        :param event_id: The event ID.
        :param timestamp: The event timestamp.
        :param data: The event data.
        :param phenomenon_name: The phenomenon name.
        :param pattern_name: The pattern name.
        :param history: The history of events.

        :raises BoboEventError: If length of phenomenon name is equal to 0.
        :raises BoboEventError: If length of pattern name is equal to 0.
        """
        super().__init__(
            event_id=event_id,
            timestamp=timestamp,
            data=data)

        if len(phenomenon_name) == 0:
            raise BoboEventError(self._EXC_PRO_LEN)

        if len(pattern_name) == 0:
            raise BoboEventError(self._EXC_PAT_LEN)

        self._phenomenon_name: str = phenomenon_name
        self._pattern_name: str = pattern_name
        self._history: BoboHistory = history

    def cast(self, dtype: type) -> 'BoboEventComplex':
        return BoboEventComplex(
            event_id=self._event_id,
            timestamp=self._timestamp,
            data=dtype(self._data),
            phenomenon_name=self._phenomenon_name,
            pattern_name=self._pattern_name,
            history=self._history
        )

    @property
    def phenomenon_name(self) -> str:
        """Get phenomenon name."""
        return self._phenomenon_name

    @property
    def pattern_name(self) -> str:
        """Get pattern name."""
        return self._pattern_name

    @property
    def history(self) -> BoboHistory:
        """Get history."""
        return self._history

    def to_json_str(self) -> str:
        return dumps({
            self.EVENT_TYPE: self.TYPE_COMPLEX,
            self.EVENT_ID: self.event_id,
            self.TIMESTAMP: self.timestamp,
            self.DATA: self.data,
            self.PHENOMENON_NAME: self.phenomenon_name,
            self.PATTERN_NAME: self.pattern_name,
            self.HISTORY: self.history
        }, default=lambda o: o.to_json_str())

    @staticmethod
    def from_json_str(j: str) -> 'BoboEventComplex':
        return BoboEventComplex.from_dict(loads(j))

    @staticmethod
    def from_dict(d: dict) -> 'BoboEventComplex':
        return BoboEventComplex(
            event_id=d[BoboEventComplex.EVENT_ID],
            timestamp=d[BoboEventComplex.TIMESTAMP],
            data=d[BoboEventComplex.DATA],
            phenomenon_name=d[BoboEventComplex.PHENOMENON_NAME],
            pattern_name=d[BoboEventComplex.PATTERN_NAME],
            history=BoboHistory.from_json_str(d[BoboEventComplex.HISTORY])
        )

    def __str__(self) -> str:
        return self.to_json_str()


class BoboEventSimple(BoboEvent):
    """
    A simple event.
    """

    TYPE_SIMPLE = "simple"

    def __init__(self,
                 event_id: str,
                 timestamp: int,
                 data: Any):
        """
        :param event_id: The event ID.
        :param timestamp: The event timestamp.
        :param data: The event data.
        """
        super().__init__(
            event_id=event_id,
            timestamp=timestamp,
            data=data)

    def cast(self, dtype: type) -> 'BoboEventSimple':
        return BoboEventSimple(
            event_id=self._event_id,
            timestamp=self._timestamp,
            data=dtype(self._data)
        )

    def to_json_str(self) -> str:
        return dumps({
            self.EVENT_TYPE: self.TYPE_SIMPLE,
            self.EVENT_ID: self.event_id,
            self.TIMESTAMP: self.timestamp,
            self.DATA: self.data
        }, default=lambda o: o.to_json_str())

    @staticmethod
    def from_json_str(j: str) -> 'BoboEventSimple':
        return BoboEventSimple.from_dict(loads(j))

    @staticmethod
    def from_dict(d: dict) -> 'BoboEventSimple':
        return BoboEventSimple(
            event_id=d[BoboEventSimple.EVENT_ID],
            timestamp=d[BoboEventSimple.TIMESTAMP],
            data=d[BoboEventSimple.DATA]
        )

    def __str__(self) -> str:
        return self.to_json_str()


class BoboEventFactory:
    """
    A BoboEvent factory that generates instances from JSON representations
    of events.
    """

    @staticmethod
    def from_json_str(j: str) -> BoboEvent:
        """
        :param j: A JSON string representation of an object of this type.
        :return: A new BoboEvent instance of its type.

        :raises BoboEventFactoryError: If `EVENT_TYPE` key is missing
            from JSON.
        :raises BoboEventFactoryError: If `EVENT_TYPE` value is an unknown
            event type.
        """
        d: dict = loads(j)

        if BoboEvent.EVENT_TYPE not in d:
            raise BoboEventFactoryError(
                "Missing key '{}'.".format(BoboEvent.EVENT_TYPE))

        if d[BoboEvent.EVENT_TYPE] == BoboEventAction.TYPE_ACTION:
            return BoboEventAction.from_dict(d)

        if d[BoboEvent.EVENT_TYPE] == BoboEventComplex.TYPE_COMPLEX:
            return BoboEventComplex.from_dict(d)

        if d[BoboEvent.EVENT_TYPE] == BoboEventSimple.TYPE_SIMPLE:
            return BoboEventSimple.from_dict(d)

        raise BoboEventFactoryError(
            "Unknown event type '{}'.".format(d[BoboEvent.EVENT_TYPE]))
