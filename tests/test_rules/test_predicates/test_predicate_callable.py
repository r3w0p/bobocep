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


def test_callable_invalid_callable():
    call = 123456

    with pytest.raises(PreconditionError):
        BoboPredicateCallable(call=call)


def test_callable_invalid_function_too_few_parameters():
    def invalid_callable_function(p):
        return True

    call = invalid_callable_function

    with pytest.raises(PreconditionError):
        BoboPredicateCallable(call=call)


def test_callable_invalid_lambda_too_few_parameters():
    call = lambda p: True

    with pytest.raises(PreconditionError):
        BoboPredicateCallable(call=call)


def test_callable_invalid_method_too_few_parameters():
    class TestInvalidClass:
        def evaluate(self, p) -> bool:
            return True

    call = TestInvalidClass().evaluate

    with pytest.raises(PreconditionError):
        BoboPredicateCallable(call=call)


def test_callable_invalid_function_too_many_parameters():
    def invalid_callable_function(p1, p2, p3):
        return True

    call = invalid_callable_function

    with pytest.raises(PreconditionError):
        BoboPredicateCallable(call=call)


def test_callable_invalid_lambda_too_many_parameters():
    call = lambda p1, p2, p3: True

    with pytest.raises(PreconditionError):
        BoboPredicateCallable(call=call)


def test_callable_invalid_method_too_many_parameters():
    class TestInvalidClass:
        def evaluate(self, p1, p2, p3) -> bool:
            return True

    call = TestInvalidClass().evaluate

    with pytest.raises(PreconditionError):
        BoboPredicateCallable(call=call)
