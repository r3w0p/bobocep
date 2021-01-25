import pytest

from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.rules.events.bobo_history import BoboHistory
from bobocep.rules.predicates.bobo_predicate_callable import \
    BoboPredicateCallable
from bobocep.rules.states.bobo_state import BoboState
from dpcontracts import PreconditionError


def test_state_valid_arguments():
    name = "test_name"
    label = "test_label"
    predicate = BoboPredicateCallable(call=lambda e, h: True)
    forbidden = False
    optional = False

    state = BoboState(
        name=name,
        label=label,
        predicate=predicate,
        forbidden=forbidden,
        optional=optional
    )

    assert state.name == name
    assert state.label == label
    assert state.predicate == predicate
    assert state.forbidden == forbidden
    assert state.optional == optional


def test_state_invalid_name():
    name = 123456
    label = "test_label"
    predicate = BoboPredicateCallable(call=lambda e, h: True)
    forbidden = False
    optional = False

    with pytest.raises(PreconditionError):
        BoboState(
            name=name,
            label=label,
            predicate=predicate,
            forbidden=forbidden,
            optional=optional
        )


def test_state_invalid_label():
    name = "test_name"
    label = 123456
    predicate = BoboPredicateCallable(call=lambda e, h: True)
    forbidden = False
    optional = False

    with pytest.raises(PreconditionError):
        BoboState(
            name=name,
            label=label,
            predicate=predicate,
            forbidden=forbidden,
            optional=optional
        )


def test_state_invalid_predicate():
    name = "test_name"
    label = "test_label"
    predicate = 123456
    forbidden = False
    optional = False

    with pytest.raises(PreconditionError):
        BoboState(
            name=name,
            label=label,
            predicate=predicate,
            forbidden=forbidden,
            optional=optional
        )


def test_state_invalid_forbidden():
    name = "test_name"
    label = "test_label"
    predicate = BoboPredicateCallable(call=lambda e, h: True)
    forbidden = "invalid_forbidden"
    optional = False

    with pytest.raises(PreconditionError):
        BoboState(
            name=name,
            label=label,
            predicate=predicate,
            forbidden=forbidden,
            optional=optional
        )


def test_state_invalid_optional():
    name = "test_name"
    label = "test_label"
    predicate = BoboPredicateCallable(call=lambda e, h: True)
    forbidden = False
    optional = "invalid_optional"

    with pytest.raises(PreconditionError):
        BoboState(
            name=name,
            label=label,
            predicate=predicate,
            forbidden=forbidden,
            optional=optional
        )


def test_state_predicate_process_true():
    call = lambda e, h: True
    state = BoboState(
        name="test_name",
        label="test_label",
        predicate=BoboPredicateCallable(call=call),
        forbidden=False,
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
        label="test_label",
        predicate=BoboPredicateCallable(call=call),
        forbidden=False,
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
        label="test_label",
        predicate=BoboPredicateCallable(call=call),
        forbidden=False,
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
        label="test_label",
        predicate=BoboPredicateCallable(call=call),
        forbidden=False,
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
