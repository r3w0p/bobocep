import pytest
from dpcontracts import PreconditionError

from bobocep.rules.events.bobo_history import BoboHistory
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.rules.predicates.bobo_predicate_callable import \
    BoboPredicateCallable
from bobocep.rules.states.bobo_state import BoboState


def test_state_valid_arguments():
    name = "test_name"
    group = "test_group"
    predicate = BoboPredicateCallable(call=lambda e, h: True)
    negated = False
    optional = False

    state = BoboState(
        name=name,
        group=group,
        predicate=predicate,
        negated=negated,
        optional=optional
    )

    assert state.name == name
    assert state.group == group
    assert state.predicate == predicate
    assert state.negated == negated
    assert state.optional == optional


def test_state_invalid_name():
    name = 123456
    group = "test_group"
    predicate = BoboPredicateCallable(call=lambda e, h: True)
    negated = False
    optional = False

    with pytest.raises(PreconditionError):
        BoboState(
            name=name,
            group=group,
            predicate=predicate,
            negated=negated,
            optional=optional
        )


def test_state_invalid_group():
    name = "test_name"
    group = 123456
    predicate = BoboPredicateCallable(call=lambda e, h: True)
    negated = False
    optional = False

    with pytest.raises(PreconditionError):
        BoboState(
            name=name,
            group=group,
            predicate=predicate,
            negated=negated,
            optional=optional
        )


def test_state_invalid_predicate():
    name = "test_name"
    group = "test_group"
    predicate = 123456
    negated = False
    optional = False

    with pytest.raises(PreconditionError):
        BoboState(
            name=name,
            group=group,
            predicate=predicate,
            negated=negated,
            optional=optional
        )


def test_state_invalid_negated():
    name = "test_name"
    group = "test_group"
    predicate = BoboPredicateCallable(call=lambda e, h: True)
    negated = "invalid_negated"
    optional = False

    with pytest.raises(PreconditionError):
        BoboState(
            name=name,
            group=group,
            predicate=predicate,
            negated=negated,
            optional=optional
        )


def test_state_invalid_optional():
    name = "test_name"
    group = "test_group"
    predicate = BoboPredicateCallable(call=lambda e, h: True)
    negated = False
    optional = "invalid_optional"

    with pytest.raises(PreconditionError):
        BoboState(
            name=name,
            group=group,
            predicate=predicate,
            negated=negated,
            optional=optional
        )


def test_state_predicate_process_true():
    call = lambda e, h: True
    state = BoboState(
        name="test_name",
        group="test_group",
        predicate=BoboPredicateCallable(call=call),
        negated=False,
        optional=False
    )

    event = PrimitiveEvent(
        event_id="test_event_id",
        timestamp=123456,
        data={}
    )
    history = BoboHistory(events={})

    assert state.process(event=event, history=history)


def test_state_predicate_process_false():
    call = lambda e, h: False
    state = BoboState(
        name="test_name",
        group="test_group",
        predicate=BoboPredicateCallable(call=call),
        negated=False,
        optional=False
    )

    event = PrimitiveEvent(
        event_id="test_event_id",
        timestamp=123456,
        data={}
    )
    history = BoboHistory(events={})

    assert not state.process(event=event, history=history)


def test_state_predicate_process_invalid_event():
    call = lambda e, h: True
    state = BoboState(
        name="test_name",
        group="test_group",
        predicate=BoboPredicateCallable(call=call),
        negated=False,
        optional=False
    )

    event = "invalid_event"
    history = BoboHistory(events={})

    with pytest.raises(PreconditionError):
        state.process(event=event, history=history)


def test_state_predicate_process_invalid_history():
    call = lambda e, h: True
    state = BoboState(
        name="test_name",
        group="test_group",
        predicate=BoboPredicateCallable(call=call),
        negated=False,
        optional=False
    )

    event = PrimitiveEvent(
        event_id="test_event_id",
        timestamp=123456,
        data={}
    )
    history = "invalid_history"

    with pytest.raises(PreconditionError):
        state.process(event=event, history=history)
