import pytest

from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.rules.events.bobo_history import BoboHistory
from bobocep.rules.predicates.bobo_predicate_callable import \
    BoboPredicateCallable
from dpcontracts import PreconditionError


def test_callable_valid_function():
    test_event_id = "test_event_id"
    test_timestamp = 123456
    test_data = {}
    test_event = PrimitiveEvent(
        event_id=test_event_id,
        timestamp=test_timestamp,
        data=test_data
    )
    test_history = BoboHistory(events={})

    def predicate_callable_function(event: BoboEvent, history: BoboHistory):
        return event.event_id == test_event_id

    call = predicate_callable_function
    predicate = BoboPredicateCallable(call=call)

    assert predicate.evaluate(test_event, test_history)


def test_callable_valid_lambda():
    test_event_id = "test_event_id"
    test_timestamp = 123456
    test_data = {}
    test_event = PrimitiveEvent(
        event_id=test_event_id,
        timestamp=test_timestamp,
        data=test_data
    )
    test_history = BoboHistory(events={})

    call = lambda e, h: e.event_id == test_event_id
    predicate = BoboPredicateCallable(call=call)

    assert predicate.evaluate(test_event, test_history)


def test_callable_valid_method():
    test_event_id = "test_event_id"
    test_timestamp = 123456
    test_data = {}
    test_event = PrimitiveEvent(
        event_id=test_event_id,
        timestamp=test_timestamp,
        data=test_data
    )
    test_history = BoboHistory(events={})

    class TestPredicateClass:
        def evaluate(self, event: BoboEvent, history: BoboHistory) -> bool:
            return event.event_id == test_event_id

    call = TestPredicateClass().evaluate
    predicate = BoboPredicateCallable(call=call)

    assert predicate.evaluate(test_event, test_history)
