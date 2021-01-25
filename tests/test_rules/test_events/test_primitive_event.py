import pytest

from bobocep.rules.events.primitive_event import PrimitiveEvent
from dpcontracts import PreconditionError


def test_primitive_valid_arguments():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}

    event = PrimitiveEvent(
        event_id=event_id,
        timestamp=timestamp,
        data=data
    )

    assert event.event_id == event_id
    assert event.timestamp == timestamp
    assert event.data == data


def test_primitive_invalid_event_id():
    event_id = 123456
    timestamp = 123456
    data = {"test_key": "test_value"}

    with pytest.raises(PreconditionError):
        PrimitiveEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data
        )


def test_primitive_invalid_timestamp():
    event_id = "test_event_id"
    timestamp = "test_invalid_timestamp"
    data = {"test_key": "test_value"}

    with pytest.raises(PreconditionError):
        PrimitiveEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data
        )


def test_primitive_invalid_data_key():
    event_id = "test_event_id"
    timestamp = 123456
    data = {123456: "test_value"}

    with pytest.raises(PreconditionError):
        PrimitiveEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data
        )


def test_primitive_invalid_data_value():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": 123456}

    with pytest.raises(PreconditionError):
        PrimitiveEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data
        )


def test_primitive_to_dict_valid():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}

    event = PrimitiveEvent(
        event_id=event_id,
        timestamp=timestamp,
        data=data
    )

    assert event.to_dict() == {
        PrimitiveEvent.EVENT_ID: event_id,
        PrimitiveEvent.TIMESTAMP: timestamp,
        PrimitiveEvent.DATA: data
    }


def test_from_dict_valid_dict():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": "test_value"}

    event_dict = {
        PrimitiveEvent.EVENT_ID: event_id,
        PrimitiveEvent.TIMESTAMP: timestamp,
        PrimitiveEvent.DATA: data
    }

    event = PrimitiveEvent.from_dict(d=event_dict)

    assert event.event_id == event_id
    assert event.timestamp == timestamp
    assert event.data == data

# todo from_dict invalid
