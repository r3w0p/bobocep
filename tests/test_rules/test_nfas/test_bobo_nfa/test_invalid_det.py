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
from tests.test_rules.test_nfas.test_bobo_nfa.helpers_bobo_nfa import *


def test_invalid_det_one_state_only():
    test_state_start = simple_state("start")

    with pytest.raises(PreconditionError):
        BoboNFA(
            name="test_nfa_name",
            states={test_state_start.name: test_state_start},
            transitions={},
            start_state_name=test_state_start.name,
            final_state_name=test_state_start.name,
            preconditions=[],
            haltconditions=[]
        )


def test_invalid_det_start_state_not_in_states():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_final.name: test_state_final
    }
    test_nfa_transitions = {
        test_state_start.name: simple_transition(test_state_final.name)
    }
    test_start_state_name = test_state_start.name
    test_final_state_name = test_state_final.name
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


def test_invalid_det_start_state_not_in_transitions():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_start.name: test_state_start,
        test_state_final.name: test_state_final
    }
    test_nfa_transitions = {}
    test_start_state_name = test_state_start.name
    test_final_state_name = test_state_final.name
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


def test_invalid_det_start_state_negated():
    test_state_start = simple_state("start", negated=True)
    test_state_final = simple_state("final")

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_start.name: test_state_start,
        test_state_final.name: test_state_final
    }
    test_nfa_transitions = {
        test_state_start.name: simple_transition(test_state_final.name)
    }
    test_start_state_name = test_state_start.name
    test_final_state_name = test_state_final.name
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


def test_invalid_det_start_state_optional():
    test_state_start = simple_state("start", optional=True)
    test_state_final = simple_state("final")

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_start.name: test_state_start,
        test_state_final.name: test_state_final
    }
    test_nfa_transitions = {
        test_state_start.name: simple_transition(test_state_final.name)
    }
    test_start_state_name = test_state_start.name
    test_final_state_name = test_state_final.name
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


def test_invalid_det_start_state_loop():
    test_state_start = simple_state("start", optional=True)
    test_state_final = simple_state("final")

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_start.name: test_state_start,
        test_state_final.name: test_state_final
    }
    test_nfa_transitions = {
        test_state_start.name: BoboTransition(
            state_names={
                test_state_start.name,
                test_state_final.name
            },
            strict=False
        )
    }
    test_start_state_name = test_state_start.name
    test_final_state_name = test_state_final.name
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


def test_invalid_det_final_state_not_in_states():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_start.name: test_state_start
    }
    test_nfa_transitions = {
        test_state_start.name: simple_transition(test_state_final.name)
    }
    test_start_state_name = test_state_start.name
    test_final_state_name = test_state_final.name
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


def test_invalid_det_final_state_in_transitions():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_after_final = simple_state("after_final")

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_start.name: test_state_start,
        test_state_final.name: test_state_final,
        test_state_after_final.name: test_state_after_final
    }
    test_nfa_transitions = {
        test_state_start.name: simple_transition(test_state_final.name),
        test_state_final.name: simple_transition(test_state_after_final.name)
    }
    test_start_state_name = test_state_start.name
    test_final_state_name = test_state_final.name
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


def test_invalid_det_final_state_negated():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final", negated=True)

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_start.name: test_state_start,
        test_state_final.name: test_state_final
    }
    test_nfa_transitions = {
        test_state_start.name: simple_transition(test_state_final.name)
    }
    test_start_state_name = test_state_start.name
    test_final_state_name = test_state_final.name
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


def test_invalid_det_final_state_optional():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final", optional=True)

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_start.name: test_state_start,
        test_state_final.name: test_state_final
    }
    test_nfa_transitions = {
        test_state_start.name: simple_transition(test_state_final.name)
    }
    test_start_state_name = test_state_start.name
    test_final_state_name = test_state_final.name
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


def test_invalid_det_second_state_not_in_states():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_second = simple_state("second")

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_start.name: test_state_start,
        test_state_final.name: test_state_final
    }
    test_nfa_transitions = {
        test_state_start.name: simple_transition(test_state_second.name),
        test_state_second.name: simple_transition(test_state_final.name)
    }
    test_start_state_name = test_state_start.name
    test_final_state_name = test_state_final.name
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


def test_invalid_det_second_state_not_in_transitions():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_second = simple_state("second")

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_start.name: test_state_start,
        test_state_final.name: test_state_final,
        test_state_second.name: test_state_second
    }
    test_nfa_transitions = {
        test_state_start.name: simple_transition(test_state_second.name)
    }
    test_start_state_name = test_state_start.name
    test_final_state_name = test_state_final.name
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


def test_invalid_det_second_state_negated():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_second = simple_state("second", negated=True)

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_start.name: test_state_start,
        test_state_final.name: test_state_final,
        test_state_second.name: test_state_second
    }
    test_nfa_transitions = {
        test_state_start.name: simple_transition(test_state_second.name),
        test_state_second.name: simple_transition(test_state_final.name)
    }
    test_start_state_name = test_state_start.name
    test_final_state_name = test_state_final.name
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


def test_invalid_det_second_state_optional():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_second = simple_state("second", optional=True)

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_start.name: test_state_start,
        test_state_final.name: test_state_final,
        test_state_second.name: test_state_second
    }
    test_nfa_transitions = {
        test_state_start.name: simple_transition(test_state_second.name),
        test_state_second.name: simple_transition(test_state_final.name)
    }
    test_start_state_name = test_state_start.name
    test_final_state_name = test_state_final.name
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


def test_invalid_det_penultimate_state_not_in_states():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_penultimate = simple_state("penultimate")

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_start.name: test_state_start,
        test_state_final.name: test_state_final
    }
    test_nfa_transitions = {
        test_state_start.name: simple_transition(test_state_penultimate.name),
        test_state_penultimate.name: simple_transition(test_state_final.name)
    }
    test_start_state_name = test_state_start.name
    test_final_state_name = test_state_final.name
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


def test_invalid_det_penultimate_state_not_in_transitions():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_penultimate = simple_state("penultimate")

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_start.name: test_state_start,
        test_state_final.name: test_state_final,
        test_state_penultimate.name: test_state_penultimate
    }
    test_nfa_transitions = {
        test_state_start.name: simple_transition(test_state_penultimate.name)
    }
    test_start_state_name = test_state_start.name
    test_final_state_name = test_state_final.name
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


def test_invalid_det_penultimate_state_negated():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_penultimate = simple_state("penultimate", negated=True)

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_start.name: test_state_start,
        test_state_final.name: test_state_final,
        test_state_penultimate.name: test_state_penultimate
    }
    test_nfa_transitions = {
        test_state_start.name: simple_transition(test_state_penultimate.name),
        test_state_penultimate.name: simple_transition(test_state_final.name)
    }
    test_start_state_name = test_state_start.name
    test_final_state_name = test_state_final.name
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


def test_invalid_det_penultimate_state_optional():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_penultimate = simple_state("penultimate", optional=True)

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_start.name: test_state_start,
        test_state_final.name: test_state_final,
        test_state_penultimate.name: test_state_penultimate
    }
    test_nfa_transitions = {
        test_state_start.name: simple_transition(test_state_penultimate.name),
        test_state_penultimate.name: simple_transition(test_state_final.name)
    }
    test_start_state_name = test_state_start.name
    test_final_state_name = test_state_final.name
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


def test_invalid_det_self_loop_only_in_transition():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_a = simple_state("a")
    test_state_b = simple_state("b")
    test_state_c = simple_state("c")

    with pytest.raises(PreconditionError):
        BoboNFA(
            name="test_nfa_name",
            states={
                test_state_start.name: test_state_start,
                test_state_final.name: test_state_final,
                test_state_a.name: test_state_a,
                test_state_b.name: test_state_b,
                test_state_c.name: test_state_c
            },
            transitions={
                test_state_start.name: simple_transition(test_state_a.name),
                test_state_a.name: simple_transition(test_state_b.name),
                test_state_b.name: BoboTransition(
                    state_names={
                        test_state_b.name
                    },
                    strict=False
                ),
                test_state_c.name: simple_transition(test_state_final.name)
            },
            start_state_name=test_state_start.name,
            final_state_name=test_state_final.name,
            preconditions=[],
            haltconditions=[]
        )


def test_invalid_det_self_transition_to_previous_state():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_a = simple_state("a")
    test_state_b = simple_state("b")
    test_state_c = simple_state("c")

    with pytest.raises(PreconditionError):
        BoboNFA(
            name="test_nfa_name",
            states={
                test_state_start.name: test_state_start,
                test_state_final.name: test_state_final,
                test_state_a.name: test_state_a,
                test_state_b.name: test_state_b,
                test_state_c.name: test_state_c
            },
            transitions={
                test_state_start.name: simple_transition(test_state_a.name),
                test_state_a.name: simple_transition(test_state_b.name),
                test_state_b.name: simple_transition(test_state_a.name),
                test_state_c.name: simple_transition(test_state_final.name)
            },
            start_state_name=test_state_start.name,
            final_state_name=test_state_final.name,
            preconditions=[],
            haltconditions=[]
        )


def test_invalid_det_no_transition_for_state():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_a = simple_state("a")
    test_state_b = simple_state("b")
    test_state_c = simple_state("c")

    with pytest.raises(PreconditionError):
        BoboNFA(
            name="test_nfa_name",
            states={
                test_state_start.name: test_state_start,
                test_state_final.name: test_state_final,
                test_state_a.name: test_state_a,
                test_state_b.name: test_state_b,
                test_state_c.name: test_state_c
            },
            transitions={
                test_state_start.name: simple_transition(test_state_a.name),
                test_state_a.name: simple_transition(test_state_b.name),
                test_state_c.name: simple_transition(test_state_final.name)
            },
            start_state_name=test_state_start.name,
            final_state_name=test_state_final.name,
            preconditions=[],
            haltconditions=[]
        )
