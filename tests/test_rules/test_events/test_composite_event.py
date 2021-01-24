import pytest

from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.primitive_event import PrimitiveEvent
from dpcontracts import PreconditionError


def test_to_dict_valid_arguments():
    history_event_event_id = "test_history_event_event_id"
    history_event_timestamp = 123456
    history_event_data = {"test_history_event_key": "test_history_event_value"}
    history_event = PrimitiveEvent(
        event_id=history_event_event_id,
        timestamp=history_event_timestamp,
        data=history_event_data
    )

    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_id = "test_nfa_id"
    history_key = "test_history_key"
    history = {history_key: [history_event]}

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
        CompositeEvent.HISTORY: {
            history_key: [{
                CompositeEvent.HISTORY_EVENT: {
                    PrimitiveEvent.EVENT_ID: history_event_event_id,
                    PrimitiveEvent.TIMESTAMP: history_event_timestamp,
                    PrimitiveEvent.DATA: history_event_data
                },
                CompositeEvent.HISTORY_EVENT_CLASS:
                    history_event.__class__.__name__
            }]
        }
    }


def test_to_dict_invalid_event_id():
    history_event_event_id = "test_history_event_event_id"
    history_event_timestamp = 123456
    history_event_data = {"test_history_event_key": "test_history_event_value"}
    history_event = PrimitiveEvent(
        event_id=history_event_event_id,
        timestamp=history_event_timestamp,
        data=history_event_data
    )

    event_id = 123456
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_id = "test_nfa_id"
    history_key = "test_history_key"
    history = {history_key: [history_event]}

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
    history_event_event_id = "test_history_event_event_id"
    history_event_timestamp = 123456
    history_event_data = {"test_history_event_key": "test_history_event_value"}
    history_event = PrimitiveEvent(
        event_id=history_event_event_id,
        timestamp=history_event_timestamp,
        data=history_event_data
    )

    event_id = "test_event_id"
    timestamp = "test_invalid_timestamp"
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_id = "test_nfa_id"
    history_key = "test_history_key"
    history = {history_key: [history_event]}

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
    history_event_event_id = "test_history_event_event_id"
    history_event_timestamp = 123456
    history_event_data = {"test_history_event_key": "test_history_event_value"}
    history_event = PrimitiveEvent(
        event_id=history_event_event_id,
        timestamp=history_event_timestamp,
        data=history_event_data
    )

    event_id = "test_event_id"
    timestamp = 123456
    data = {123456: "test_value"}
    event_name = "test_event_name"
    nfa_id = "test_nfa_id"
    history_key = "test_history_key"
    history = {history_key: [history_event]}

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
    history_event_event_id = "test_history_event_event_id"
    history_event_timestamp = 123456
    history_event_data = {"test_history_event_key": "test_history_event_value"}
    history_event = PrimitiveEvent(
        event_id=history_event_event_id,
        timestamp=history_event_timestamp,
        data=history_event_data
    )

    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": 123456}
    event_name = "test_event_name"
    nfa_id = "test_nfa_id"
    history_key = "test_history_key"
    history = {history_key: [history_event]}

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
    history_event_event_id = "test_history_event_event_id"
    history_event_timestamp = 123456
    history_event_data = {"test_history_event_key": "test_history_event_value"}
    history_event = PrimitiveEvent(
        event_id=history_event_event_id,
        timestamp=history_event_timestamp,
        data=history_event_data
    )

    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = 123456
    nfa_id = "test_nfa_id"
    history_key = "test_history_key"
    history = {history_key: [history_event]}

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
    history_event_event_id = "test_history_event_event_id"
    history_event_timestamp = 123456
    history_event_data = {"test_history_event_key": "test_history_event_value"}
    history_event = PrimitiveEvent(
        event_id=history_event_event_id,
        timestamp=history_event_timestamp,
        data=history_event_data
    )

    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_id = 123456
    history_key = "test_history_key"
    history = {history_key: [history_event]}

    with pytest.raises(PreconditionError):
        CompositeEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data,
            event_name=event_name,
            nfa_id=nfa_id,
            history=history
        )


def test_to_dict_invalid_history_key():
    history_event_event_id = "test_history_event_event_id"
    history_event_timestamp = 123456
    history_event_data = {"test_history_event_key": "test_history_event_value"}
    history_event = PrimitiveEvent(
        event_id=history_event_event_id,
        timestamp=history_event_timestamp,
        data=history_event_data
    )

    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_id = "test_nfa_id"
    history_key = 123456
    history = {history_key: [history_event]}

    with pytest.raises(PreconditionError):
        CompositeEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data,
            event_name=event_name,
            nfa_id=nfa_id,
            history=history
        )


def test_to_dict_invalid_history_value():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_id = "test_nfa_id"
    history_key = "test_history_key"
    history = {history_key: 123456}

    with pytest.raises(PreconditionError):
        CompositeEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data,
            event_name=event_name,
            nfa_id=nfa_id,
            history=history
        )


def test_to_dict_invalid_history_list_value():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}
    event_name = "test_event_name"
    nfa_id = "test_nfa_id"
    history_key = "test_history_key"
    history = {history_key: [123456]}

    with pytest.raises(PreconditionError):
        CompositeEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data,
            event_name=event_name,
            nfa_id=nfa_id,
            history=history
        )
