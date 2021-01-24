import pytest

from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.bobo_history import BoboHistory
from dpcontracts import PreconditionError


def test_to_dict_valid_arguments_history_empty():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_id = "test_nfa_id"
    history = BoboHistory(events={})

    event = CompositeEvent(
        event_id=event_id,
        timestamp=timestamp,
        data=data,
        event_name=event_name,
        nfa_id=nfa_id,
        history=history
    )

    assert event.to_dict() == {
        CompositeEvent.EVENT_ID: event_id,
        CompositeEvent.TIMESTAMP: timestamp,
        CompositeEvent.DATA: data,
        CompositeEvent.EVENT_NAME: event_name,
        CompositeEvent.NFA_ID: nfa_id,
        CompositeEvent.HISTORY: history.to_dict()
    }


def test_to_dict_valid_arguments_history_key_empty():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_id = "test_nfa_id"
    history = BoboHistory(events={})

    event = CompositeEvent(
        event_id=event_id,
        timestamp=timestamp,
        data=data,
        event_name=event_name,
        nfa_id=nfa_id,
        history=history
    )

    assert event.to_dict() == {
        CompositeEvent.EVENT_ID: event_id,
        CompositeEvent.TIMESTAMP: timestamp,
        CompositeEvent.DATA: data,
        CompositeEvent.EVENT_NAME: event_name,
        CompositeEvent.NFA_ID: nfa_id,
        CompositeEvent.HISTORY: history.to_dict()
    }


def test_to_dict_valid_arguments_history_not_empty():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_id = "test_nfa_id"
    history = BoboHistory(events={})

    event = CompositeEvent(
        event_id=event_id,
        timestamp=timestamp,
        data=data,
        event_name=event_name,
        nfa_id=nfa_id,
        history=history
    )

    assert event.to_dict() == {
        CompositeEvent.EVENT_ID: event_id,
        CompositeEvent.TIMESTAMP: timestamp,
        CompositeEvent.DATA: data,
        CompositeEvent.EVENT_NAME: event_name,
        CompositeEvent.NFA_ID: nfa_id,
        CompositeEvent.HISTORY: history.to_dict()
    }


def test_to_dict_valid_arguments_data_empty():
    event_id = "test_event_id"
    timestamp = 123456
    data = {}
    event_name = "test_event_name"
    nfa_id = "test_nfa_id"
    history = BoboHistory(events={})

    event = CompositeEvent(
        event_id=event_id,
        timestamp=timestamp,
        data=data,
        event_name=event_name,
        nfa_id=nfa_id,
        history=history
    )

    assert event.to_dict() == {
        CompositeEvent.EVENT_ID: event_id,
        CompositeEvent.TIMESTAMP: timestamp,
        CompositeEvent.DATA: data,
        CompositeEvent.EVENT_NAME: event_name,
        CompositeEvent.NFA_ID: nfa_id,
        CompositeEvent.HISTORY: history.to_dict()
    }


def test_to_dict_invalid_event_id():
    event_id = 123456
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_id = "test_nfa_id"
    history = BoboHistory(events={})

    with pytest.raises(PreconditionError):
        CompositeEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data,
            event_name=event_name,
            nfa_id=nfa_id,
            history=history
        )


def test_to_dict_invalid_timestamp():
    event_id = "test_event_id"
    timestamp = "test_invalid_timestamp"
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_id = "test_nfa_id"
    history = BoboHistory(events={})

    with pytest.raises(PreconditionError):
        CompositeEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data,
            event_name=event_name,
            nfa_id=nfa_id,
            history=history
        )


def test_to_dict_invalid_data_key():
    event_id = "test_event_id"
    timestamp = 123456
    data = {123456: "test_value"}
    event_name = "test_event_name"
    nfa_id = "test_nfa_id"
    history = BoboHistory(events={})

    with pytest.raises(PreconditionError):
        CompositeEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data,
            event_name=event_name,
            nfa_id=nfa_id,
            history=history
        )


def test_to_dict_invalid_data_value():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": 123456}
    event_name = "test_event_name"
    nfa_id = "test_nfa_id"
    history = BoboHistory(events={})

    with pytest.raises(PreconditionError):
        CompositeEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data,
            event_name=event_name,
            nfa_id=nfa_id,
            history=history
        )


def test_to_dict_invalid_event_name():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = 123456
    nfa_id = "test_nfa_id"
    history = BoboHistory(events={})

    with pytest.raises(PreconditionError):
        CompositeEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data,
            event_name=event_name,
            nfa_id=nfa_id,
            history=history
        )


def test_to_dict_invalid_nfa_id():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_id = 123456
    history = BoboHistory(events={})

    with pytest.raises(PreconditionError):
        CompositeEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data,
            event_name=event_name,
            nfa_id=nfa_id,
            history=history
        )


def test_to_dict_invalid_history():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_id = "test_nfa_id"
    history = 123456

    with pytest.raises(PreconditionError):
        CompositeEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data,
            event_name=event_name,
            nfa_id=nfa_id,
            history=history
        )


def test_from_dict_valid_dict():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_id = "test_nfa_id"
    history = {}

    event_dict = {
        CompositeEvent.EVENT_ID: event_id,
        CompositeEvent.TIMESTAMP: timestamp,
        CompositeEvent.DATA: data,
        CompositeEvent.EVENT_NAME: event_name,
        CompositeEvent.NFA_ID: nfa_id,
        CompositeEvent.HISTORY: history
    }

    event = CompositeEvent.from_dict(d=event_dict)

    assert event.event_id == event_id
    assert event.timestamp == timestamp
    assert event.data == data
    assert event.event_name == event_name
    assert event.nfa_id == nfa_id
    assert isinstance(event.history, BoboHistory)
