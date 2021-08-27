import pytest

from bobocep.rules.events.bobo_history import BoboHistory
from bobocep.rules.events.primitive_event import PrimitiveEvent
from dpcontracts import PreconditionError


def test_history_valid_arguments():
    history_event = PrimitiveEvent(
        event_id="test_history_event",
        timestamp=123456,
        data={}
    )

    event_key = "test_event_key"
    events = {event_key: [history_event]}
    history = BoboHistory(events=events)

    assert history.events == events


def test_history_invalid_argument_events():
    events = "invalid_events"

    with pytest.raises(PreconditionError):
        BoboHistory(events=events)


def test_history_first_and_last_same_event():
    history_event = PrimitiveEvent(
        event_id="test_history_event",
        timestamp=123456,
        data={}
    )

    event_key = "test_event_key"
    events = {event_key: [history_event]}
    history = BoboHistory(events=events)

    assert history.first == history.last


def test_history_first_and_last_two_events_two_keys():
    history_event_1 = PrimitiveEvent(
        event_id="test_history_event_1",
        timestamp=123456,
        data={}
    )

    history_event_2 = PrimitiveEvent(
        event_id="test_history_event_2",
        timestamp=987654,
        data={}
    )

    event_key_1 = "test_event_key_1"
    event_key_2 = "test_event_key_2"
    events = {
        event_key_1: [history_event_1],
        event_key_2: [history_event_2]
    }
    history = BoboHistory(events=events)

    assert history.first == history_event_1
    assert history.last == history_event_2


def test_history_first_and_last_two_events_one_key():
    history_event_1 = PrimitiveEvent(
        event_id="test_history_event_1",
        timestamp=123456,
        data={}
    )

    history_event_2 = PrimitiveEvent(
        event_id="test_history_event_2",
        timestamp=987654,
        data={}
    )

    event_key = "test_event_key"
    events = {
        event_key: [history_event_1, history_event_2]
    }
    history = BoboHistory(events=events)

    assert history.first == history_event_1
    assert history.last == history_event_2
