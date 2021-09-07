import pytest
from dpcontracts import PreconditionError

from bobocep.rules.events.primitive_event import PrimitiveEvent


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


def test_primitive_invalid_argument_event_id():
    event_id = 123456
    timestamp = 123456
    data = {"test_key": "test_value"}

    with pytest.raises(PreconditionError):
        PrimitiveEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data
        )


def test_primitive_invalid_argument_timestamp():
    event_id = "test_event_id"
    timestamp = "test_invalid_timestamp"
    data = {"test_key": "test_value"}

    with pytest.raises(PreconditionError):
        PrimitiveEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data
        )


def test_primitive_invalid_argument_data_key():
    event_id = "test_event_id"
    timestamp = 123456
    data = {123456: "test_value"}

    with pytest.raises(PreconditionError):
        PrimitiveEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data
        )


def test_primitive_invalid_argument_data_value():
    event_id = "test_event_id"
    timestamp = 123456
    data = {"test_key": 123456}

    with pytest.raises(PreconditionError):
        PrimitiveEvent(
            event_id=event_id,
            timestamp=timestamp,
            data=data
        )
