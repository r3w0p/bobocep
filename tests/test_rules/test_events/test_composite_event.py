import pytest

from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.bobo_history import BoboHistory
from dpcontracts import PreconditionError


def test_composite_valid_arguments():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_name = "test_nfa_name"
    history = BoboHistory(events={})

    event = CompositeEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data,
            event_name=event_name,
            nfa_name=nfa_name,
            history=history
        )

    assert event.event_id == event_id
    assert event.timestamp == timestamp
    assert event.data == data
    assert event.event_name == event_name
    assert event.nfa_name == nfa_name
    assert event.history == history


def test_composite_invalid_argument_event_id():
    event_id = 123456
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_name = "test_nfa_name"
    history = BoboHistory(events={})

    with pytest.raises(PreconditionError):
        CompositeEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data,
            event_name=event_name,
            nfa_name=nfa_name,
            history=history
        )


def test_composite_invalid_argument_timestamp():
    event_id = "test_event_id"
    timestamp = "test_invalid_timestamp"
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_name = "test_nfa_name"
    history = BoboHistory(events={})

    with pytest.raises(PreconditionError):
        CompositeEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data,
            event_name=event_name,
            nfa_name=nfa_name,
            history=history
        )


def test_composite_invalid_argument_data_key():
    event_id = "test_event_id"
    timestamp = 123456
    data = {123456: "test_value"}
    event_name = "test_event_name"
    nfa_name = "test_nfa_name"
    history = BoboHistory(events={})

    with pytest.raises(PreconditionError):
        CompositeEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data,
            event_name=event_name,
            nfa_name=nfa_name,
            history=history
        )


def test_composite_invalid_argument_data_value():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": 123456}
    event_name = "test_event_name"
    nfa_name = "test_nfa_name"
    history = BoboHistory(events={})

    with pytest.raises(PreconditionError):
        CompositeEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data,
            event_name=event_name,
            nfa_name=nfa_name,
            history=history
        )


def test_composite_invalid_argument_event_name():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = 123456
    nfa_name = "test_nfa_name"
    history = BoboHistory(events={})

    with pytest.raises(PreconditionError):
        CompositeEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data,
            event_name=event_name,
            nfa_name=nfa_name,
            history=history
        )


def test_composite_invalid_argument_nfa_name():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_name = 123456
    history = BoboHistory(events={})

    with pytest.raises(PreconditionError):
        CompositeEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data,
            event_name=event_name,
            nfa_name=nfa_name,
            history=history
        )


def test_composite_invalid_argument_history():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_name = "test_nfa_name"
    history = 123456

    with pytest.raises(PreconditionError):
        CompositeEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data,
            event_name=event_name,
            nfa_name=nfa_name,
            history=history
        )


def test_composite_to_dict_valid_history_empty():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_name = "test_nfa_name"
    history = BoboHistory(events={})

    event = CompositeEvent(
        event_id=event_id,
        timestamp=timestamp,
        data=data,
        event_name=event_name,
        nfa_name=nfa_name,
        history=history
    )

    assert event.to_dict() == {
        CompositeEvent.EVENT_ID: event_id,
        CompositeEvent.TIMESTAMP: timestamp,
        CompositeEvent.DATA: data,
        CompositeEvent.EVENT_NAME: event_name,
        CompositeEvent.NFA_NAME: nfa_name,
        CompositeEvent.HISTORY: history.to_dict()
    }


def test_composite_to_dict_valid_history_key_empty():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_name = "test_nfa_name"
    history = BoboHistory(events={})

    event = CompositeEvent(
        event_id=event_id,
        timestamp=timestamp,
        data=data,
        event_name=event_name,
        nfa_name=nfa_name,
        history=history
    )

    assert event.to_dict() == {
        CompositeEvent.EVENT_ID: event_id,
        CompositeEvent.TIMESTAMP: timestamp,
        CompositeEvent.DATA: data,
        CompositeEvent.EVENT_NAME: event_name,
        CompositeEvent.NFA_NAME: nfa_name,
        CompositeEvent.HISTORY: history.to_dict()
    }


def test_composite_to_dict_valid_history_not_empty():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_name = "test_nfa_name"
    history = BoboHistory(events={})

    event = CompositeEvent(
        event_id=event_id,
        timestamp=timestamp,
        data=data,
        event_name=event_name,
        nfa_name=nfa_name,
        history=history
    )

    assert event.to_dict() == {
        CompositeEvent.EVENT_ID: event_id,
        CompositeEvent.TIMESTAMP: timestamp,
        CompositeEvent.DATA: data,
        CompositeEvent.EVENT_NAME: event_name,
        CompositeEvent.NFA_NAME: nfa_name,
        CompositeEvent.HISTORY: history.to_dict()
    }


def test_composite_to_dict_valid_data_empty():
    event_id = "test_event_id"
    timestamp = 123456
    data = {}
    event_name = "test_event_name"
    nfa_name = "test_nfa_name"
    history = BoboHistory(events={})

    event = CompositeEvent(
        event_id=event_id,
        timestamp=timestamp,
        data=data,
        event_name=event_name,
        nfa_name=nfa_name,
        history=history
    )

    assert event.to_dict() == {
        CompositeEvent.EVENT_ID: event_id,
        CompositeEvent.TIMESTAMP: timestamp,
        CompositeEvent.DATA: data,
        CompositeEvent.EVENT_NAME: event_name,
        CompositeEvent.NFA_NAME: nfa_name,
        CompositeEvent.HISTORY: history.to_dict()
    }


def test_composite_from_dict_valid():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_name = "test_nfa_name"
    history = {}

    event_dict = {
        CompositeEvent.EVENT_ID: event_id,
        CompositeEvent.TIMESTAMP: timestamp,
        CompositeEvent.DATA: data,
        CompositeEvent.EVENT_NAME: event_name,
        CompositeEvent.NFA_NAME: nfa_name,
        CompositeEvent.HISTORY: history
    }

    event = CompositeEvent.from_dict(d=event_dict)

    assert event.event_id == event_id
    assert event.timestamp == timestamp
    assert event.data == data
    assert event.event_name == event_name
    assert event.nfa_name == nfa_name
    assert isinstance(event.history, BoboHistory)

# todo from_dict test_invalid
