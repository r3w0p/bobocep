import pytest

from bobocep.rules.states.bobo_transition import BoboTransition
from dpcontracts import PreconditionError


def test_transition_valid_arguments_state_names_not_empty():
    name = "test_name"
    state_names = [name]
    strict = True

    transition = BoboTransition(
        state_names=state_names,
        strict=strict
    )

    assert transition.state_names == state_names
    assert transition.strict == strict


def test_transition_valid_arguments_state_names_empty():
    state_names = []
    strict = True

    transition = BoboTransition(
        state_names=state_names,
        strict=strict
    )

    assert transition.state_names == state_names
    assert transition.strict == strict


def test_transition_invalid_argument_state_names():
    state_names = "invalid_state_names"
    strict = True

    with pytest.raises(PreconditionError):
        BoboTransition(
            state_names=state_names,
            strict=strict
        )


def test_transition_invalid_argument_strict():
    name = "test_name"
    state_names = [name]
    strict = "invalid_strict"

    with pytest.raises(PreconditionError):
        BoboTransition(
            state_names=state_names,
            strict=strict
        )


def test_transition_to_dict_valid():
    name = "test_name"
    state_names = [name]
    strict = True

    transition = BoboTransition(
        state_names=state_names,
        strict=strict
    )

    assert transition.to_dict() == {
        BoboTransition.STATE_NAMES: state_names,
        BoboTransition.STRICT: strict
    }


def test_transition_from_dict_valid():
    name = "test_name"
    state_names = [name]
    strict = True

    transition_dict = {
        BoboTransition.STATE_NAMES: state_names,
        BoboTransition.STRICT: strict
    }

    transition = BoboTransition.from_dict(d=transition_dict)

    assert transition.state_names == state_names
    assert transition.strict == strict

# todo from_dict invalid
