import pytest

from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.states.bobo_state import BoboState
from bobocep.rules.states.bobo_transition import BoboTransition
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.rules.events.bobo_history import BoboHistory
from bobocep.rules.predicates.bobo_predicate_callable import \
    BoboPredicateCallable
from bobocep.rules.nfas.bobo_nfa import BoboNFA
from dpcontracts import PreconditionError


def test_nfa_valid_arguments_one_state():
    test_state_name = "test_state_name"
    test_state_label = "test_state_label"
    test_state = BoboState(
        name=test_state_name,
        label=test_state_label,
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        forbidden=False,
        optional=False
    )

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_name: test_state
    }
    test_nfa_transitions = {}
    test_start_state_name = test_state_name
    test_final_state_name = test_state_name
    test_preconditions = []
    test_haltconditions = []

    test_nfa = BoboNFA(
        name=test_nfa_name,
        states=test_nfa_states,
        transitions=test_nfa_transitions,
        start_state_name=test_start_state_name,
        final_state_name=test_final_state_name,
        preconditions=test_preconditions,
        haltconditions=test_haltconditions
    )

    assert test_nfa.name == test_nfa_name
    assert test_nfa.states == test_nfa_states
    assert test_nfa.transitions == test_nfa_transitions
    assert test_nfa.start_state == test_state
    assert test_nfa.final_state == test_state
    assert test_nfa.preconditions == test_preconditions
    assert test_nfa.haltconditions == test_haltconditions


def test_nfa_valid_arguments_two_states():
    test_state_one_name = "test_state_one_name"
    test_state_one_label = "test_state_one_label"
    test_state_one = BoboState(
        name=test_state_one_name,
        label=test_state_one_label,
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        forbidden=False,
        optional=False
    )

    test_state_two_name = "test_state_two_name"
    test_state_two_label = "test_state_two_label"
    test_state_two = BoboState(
        name=test_state_two_name,
        label=test_state_two_label,
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        forbidden=False,
        optional=False
    )

    test_transition_one_two = BoboTransition(
        state_names={test_state_two_name},
        strict=False
    )

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_one_name: test_state_one,
        test_state_two_name: test_state_two
    }
    test_nfa_transitions = {
        test_state_one_name: test_transition_one_two
    }
    test_start_state_name = test_state_one_name
    test_final_state_name = test_state_two_name
    test_preconditions = []
    test_haltconditions = []

    test_nfa = BoboNFA(
        name=test_nfa_name,
        states=test_nfa_states,
        transitions=test_nfa_transitions,
        start_state_name=test_start_state_name,
        final_state_name=test_final_state_name,
        preconditions=test_preconditions,
        haltconditions=test_haltconditions
    )

    assert test_nfa.name == test_nfa_name
    assert test_nfa.states == test_nfa_states
    assert test_nfa.transitions == test_nfa_transitions
    assert test_nfa.start_state == test_state_one
    assert test_nfa.final_state == test_state_two
    assert test_nfa.preconditions == test_preconditions
    assert test_nfa.haltconditions == test_haltconditions


def test_nfa_invalid_transition_for_final_state():
    test_state_one_name = "test_state_one_name"
    test_state_one_label = "test_state_one_label"
    test_state_one = BoboState(
        name=test_state_one_name,
        label=test_state_one_label,
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        forbidden=False,
        optional=False
    )

    test_state_two_name = "test_state_two_name"
    test_state_two_label = "test_state_two_label"
    test_state_two = BoboState(
        name=test_state_two_name,
        label=test_state_two_label,
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        forbidden=False,
        optional=False
    )

    test_state_three_name = "test_state_three_name"
    test_state_three_label = "test_state_three_label"
    test_state_three = BoboState(
        name=test_state_three_name,
        label=test_state_three_label,
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        forbidden=False,
        optional=False
    )

    test_transition_one_two = BoboTransition(
        state_names={test_state_two_name},
        strict=False
    )

    test_transition_two_three = BoboTransition(
        state_names={test_state_three_name},
        strict=False
    )

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_one_name: test_state_one,
        test_state_two_name: test_state_two,
        test_state_three_name: test_state_three
    }
    test_nfa_transitions = {
        test_state_one_name: test_transition_one_two,
        test_state_two_name: test_transition_two_three
    }
    test_start_state_name = test_state_one_name
    test_final_state_name = test_state_two_name
    test_preconditions = []
    test_haltconditions = []

    with pytest.raises(PreconditionError):
        BoboNFA(
            name=test_nfa_name,
            states=test_nfa_states,
            transitions=test_nfa_transitions,
            start_state_name=test_start_state_name,
            final_state_name=test_final_state_name,
            preconditions=test_preconditions,
            haltconditions=test_haltconditions
        )


def test_nfa_invalid_no_transition_for_state():
    test_state_one_name = "test_state_one_name"
    test_state_one_label = "test_state_one_label"
    test_state_one = BoboState(
        name=test_state_one_name,
        label=test_state_one_label,
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        forbidden=False,
        optional=False
    )

    test_state_two_name = "test_state_two_name"
    test_state_two_label = "test_state_two_label"
    test_state_two = BoboState(
        name=test_state_two_name,
        label=test_state_two_label,
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        forbidden=False,
        optional=False
    )

    test_state_three_name = "test_state_three_name"
    test_state_three_label = "test_state_three_label"
    test_state_three = BoboState(
        name=test_state_three_name,
        label=test_state_three_label,
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        forbidden=False,
        optional=False
    )

    test_transition_one_two = BoboTransition(
        state_names={test_state_two_name},
        strict=False
    )

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_one_name: test_state_one,
        test_state_two_name: test_state_two,
        test_state_three_name: test_state_three
    }
    test_nfa_transitions = {
        test_state_one_name: test_transition_one_two
    }
    test_start_state_name = test_state_one_name
    test_final_state_name = test_state_three_name
    test_preconditions = []
    test_haltconditions = []

    with pytest.raises(PreconditionError):
        BoboNFA(
            name=test_nfa_name,
            states=test_nfa_states,
            transitions=test_nfa_transitions,
            start_state_name=test_start_state_name,
            final_state_name=test_final_state_name,
            preconditions=test_preconditions,
            haltconditions=test_haltconditions
        )


def test_nfa_invalid_transition_to_previous_state():
    test_state_one_name = "test_state_one_name"
    test_state_one_label = "test_state_one_label"
    test_state_one = BoboState(
        name=test_state_one_name,
        label=test_state_one_label,
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        forbidden=False,
        optional=False
    )

    test_state_two_name = "test_state_two_name"
    test_state_two_label = "test_state_two_label"
    test_state_two = BoboState(
        name=test_state_two_name,
        label=test_state_two_label,
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        forbidden=False,
        optional=False
    )

    test_state_three_name = "test_state_three_name"
    test_state_three_label = "test_state_three_label"
    test_state_three = BoboState(
        name=test_state_three_name,
        label=test_state_three_label,
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        forbidden=False,
        optional=False
    )

    test_state_four_name = "test_state_four_name"
    test_state_four_label = "test_state_four_label"
    test_state_four = BoboState(
        name=test_state_four_name,
        label=test_state_four_label,
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        forbidden=False,
        optional=False
    )

    test_transition_one_two = BoboTransition(
        state_names={test_state_two_name},
        strict=False
    )

    test_transition_two_three = BoboTransition(
        state_names={test_state_three_name},
        strict=False
    )

    test_transition_three_two = BoboTransition(
        state_names={test_state_two_name},
        strict=False
    )

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_one_name: test_state_one,
        test_state_two_name: test_state_two,
        test_state_three_name: test_state_three,
        test_state_four_name: test_state_four
    }
    test_nfa_transitions = {
        test_state_one_name: test_transition_one_two,
        test_state_two_name: test_transition_two_three,
        test_state_three_name: test_transition_three_two
    }
    test_start_state_name = test_state_one_name
    test_final_state_name = test_state_four_name
    test_preconditions = []
    test_haltconditions = []

    with pytest.raises(PreconditionError):
        BoboNFA(
            name=test_nfa_name,
            states=test_nfa_states,
            transitions=test_nfa_transitions,
            start_state_name=test_start_state_name,
            final_state_name=test_final_state_name,
            preconditions=test_preconditions,
            haltconditions=test_haltconditions
        )


def test_nfa_invalid_transition_to_unknown_state():
    test_state_one_name = "test_state_one_name"
    test_state_one_label = "test_state_one_label"
    test_state_one = BoboState(
        name=test_state_one_name,
        label=test_state_one_label,
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        forbidden=False,
        optional=False
    )

    test_state_two_name = "test_state_two_name"
    test_state_two_label = "test_state_two_label"
    test_state_two = BoboState(
        name=test_state_two_name,
        label=test_state_two_label,
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        forbidden=False,
        optional=False
    )

    test_state_three_name = "test_state_three_name"
    test_state_three_label = "test_state_three_label"
    test_state_three = BoboState(
        name=test_state_three_name,
        label=test_state_three_label,
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        forbidden=False,
        optional=False
    )

    test_state_four_name = "test_state_four_name"
    test_state_four_label = "test_state_four_label"
    test_state_four = BoboState(
        name=test_state_four_name,
        label=test_state_four_label,
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        forbidden=False,
        optional=False
    )

    test_transition_one_two = BoboTransition(
        state_names={test_state_two_name},
        strict=False
    )

    test_transition_two_three = BoboTransition(
        state_names={test_state_three_name},
        strict=False
    )

    test_state_unknown_name = "test_state_unknown_name"
    test_transition_three_unknown = BoboTransition(
        state_names={test_state_unknown_name},
        strict=False
    )

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_one_name: test_state_one,
        test_state_two_name: test_state_two,
        test_state_three_name: test_state_three,
        test_state_four_name: test_state_four
    }
    test_nfa_transitions = {
        test_state_one_name: test_transition_one_two,
        test_state_two_name: test_transition_two_three,
        test_state_three_name: test_transition_three_unknown
    }
    test_start_state_name = test_state_one_name
    test_final_state_name = test_state_four_name
    test_preconditions = []
    test_haltconditions = []

    with pytest.raises(PreconditionError):
        BoboNFA(
            name=test_nfa_name,
            states=test_nfa_states,
            transitions=test_nfa_transitions,
            start_state_name=test_start_state_name,
            final_state_name=test_final_state_name,
            preconditions=test_preconditions,
            haltconditions=test_haltconditions
        )


def test_nfa_invalid_self_loop_transition_only():
    test_state_one_name = "test_state_one_name"
    test_state_one_label = "test_state_one_label"
    test_state_one = BoboState(
        name=test_state_one_name,
        label=test_state_one_label,
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        forbidden=False,
        optional=False
    )

    test_state_two_name = "test_state_two_name"
    test_state_two_label = "test_state_two_label"
    test_state_two = BoboState(
        name=test_state_two_name,
        label=test_state_two_label,
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        forbidden=False,
        optional=False
    )

    test_state_three_name = "test_state_three_name"
    test_state_three_label = "test_state_three_label"
    test_state_three = BoboState(
        name=test_state_three_name,
        label=test_state_three_label,
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        forbidden=False,
        optional=False
    )

    test_state_four_name = "test_state_four_name"
    test_state_four_label = "test_state_four_label"
    test_state_four = BoboState(
        name=test_state_four_name,
        label=test_state_four_label,
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        forbidden=False,
        optional=False
    )

    test_transition_one_two = BoboTransition(
        state_names={test_state_two_name},
        strict=False
    )

    test_transition_two_three = BoboTransition(
        state_names={test_state_three_name},
        strict=False
    )

    test_transition_three_three = BoboTransition(
        state_names={test_state_three_name},
        strict=False
    )

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_one_name: test_state_one,
        test_state_two_name: test_state_two,
        test_state_three_name: test_state_three,
        test_state_four_name: test_state_four
    }
    test_nfa_transitions = {
        test_state_one_name: test_transition_one_two,
        test_state_two_name: test_transition_two_three,
        test_state_three_name: test_transition_three_three
    }
    test_start_state_name = test_state_one_name
    test_final_state_name = test_state_four_name
    test_preconditions = []
    test_haltconditions = []

    with pytest.raises(PreconditionError):
        BoboNFA(
            name=test_nfa_name,
            states=test_nfa_states,
            transitions=test_nfa_transitions,
            start_state_name=test_start_state_name,
            final_state_name=test_final_state_name,
            preconditions=test_preconditions,
            haltconditions=test_haltconditions
        )
