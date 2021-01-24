import pytest

from bobocep.rules.events.bobo_history import BoboHistory
from bobocep.rules.events.primitive_event import PrimitiveEvent


def test_to_dict_valid_arguments_history_empty():
    events = {}
    history = BoboHistory(events=events)

    assert history.to_dict() == {}


def test_to_dict_valid_arguments_history_key_empty():
    event_key = "test_event_key"
    events = {event_key: []}
    history = BoboHistory(events=events)

    assert history.to_dict() == {
        event_key: []
    }


def test_to_dict_valid_arguments_history_not_empty():
    history_event_event_id = "test_event_history_event_id"
    history_event_timestamp = 123456
    history_event_data = {}
    history_event = PrimitiveEvent(
        event_id=history_event_event_id,
        timestamp=history_event_timestamp,
        data=history_event_data
    )

    event_key = "test_event_key"
    events = {event_key: [history_event]}
    history = BoboHistory(events=events)

    assert history.to_dict() == {
        event_key: [{
            BoboHistory.HISTORY_EVENT: {
                PrimitiveEvent.EVENT_ID: history_event_event_id,
                PrimitiveEvent.TIMESTAMP: history_event_timestamp,
                PrimitiveEvent.DATA: history_event_data
            },
            BoboHistory.HISTORY_EVENT_MODULE: PrimitiveEvent.__module__,
            BoboHistory.HISTORY_EVENT_CLASS: PrimitiveEvent.__name__
        }]
    }


def test_to_dict_history_first_last_one_event():
    history_event = PrimitiveEvent(
        event_id="test_history_event",
        timestamp=123456,
        data={}
    )

    event_key = "test_event_key"
    events = {event_key: [history_event]}
    history = BoboHistory(events=events)

    assert history.first == history.last


def test_to_dict_history_first_last_two_events_two_keys():
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


def test_to_dict_history_first_last_two_events_one_key():
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


def test_from_dict_valid_dict_one_primitive():
    history_event_event_id = "test_event_history_event_id"
    history_event_timestamp = 123456
    history_event_data = {}
    event_key = "test_event_key"

    event_dict = {
        event_key: [{
            BoboHistory.HISTORY_EVENT: {
                PrimitiveEvent.EVENT_ID: history_event_event_id,
                PrimitiveEvent.TIMESTAMP: history_event_timestamp,
                PrimitiveEvent.DATA: history_event_data
            },
            BoboHistory.HISTORY_EVENT_MODULE: PrimitiveEvent.__module__,
            BoboHistory.HISTORY_EVENT_CLASS: PrimitiveEvent.__name__
        }]
    }

    history = BoboHistory.from_dict(d=event_dict)

    assert event_key in history.events
    assert len(history.events[event_key]) == 1
    assert isinstance(history.events[event_key][0], PrimitiveEvent)
