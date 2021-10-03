from bobocep.rules.nfas.bobo_nfa import BoboNFA
from tests.test_rules.test_nfas.test_bobo_nfa.helpers_bobo_nfa import *


def test_invalid_det_one_state_only():
    test_state_start = simple_state("start")

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_start.name: test_state_start
    }
    test_nfa_transitions = {}
    test_start_state_name = test_state_start.name
    test_final_state_name = test_state_start.name
    test_preconditions = set()
    test_haltconditions = set()

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
    assert test_nfa.start_state == test_state_start
    assert test_nfa.final_state == test_state_start
    assert test_nfa.preconditions == test_preconditions
    assert test_nfa.haltconditions == test_haltconditions


def test_valid_det_start_final():
    test_state_start = simple_state("start")
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
    test_preconditions = set()
    test_haltconditions = set()

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
    assert test_nfa.start_state == test_state_start
    assert test_nfa.final_state == test_state_final
    assert test_nfa.preconditions == test_preconditions
    assert test_nfa.haltconditions == test_haltconditions


def test_valid_det_start_a_final():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_a = simple_state("a")

    test_nfa = BoboNFA(
        name="test_nfa_name",
        states={
            test_state_start.name: test_state_start,
            test_state_final.name: test_state_final,
            test_state_a.name: test_state_a
        },
        transitions={
            test_state_start.name: simple_transition(test_state_a.name),
            test_state_a.name: simple_transition(test_state_final.name)
        },
        start_state_name=test_state_start.name,
        final_state_name=test_state_final.name,
        preconditions=set(),
        haltconditions=set()
    )

    assert test_nfa.start_state == test_state_start
    assert test_nfa.final_state == test_state_final


def test_valid_det_start_a_b_c_final():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_a = simple_state("a")
    test_state_b = simple_state("b")
    test_state_c = simple_state("c")

    test_nfa = BoboNFA(
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
            test_state_b.name: simple_transition(test_state_c.name),
            test_state_c.name: simple_transition(test_state_final.name)
        },
        start_state_name=test_state_start.name,
        final_state_name=test_state_final.name,
        preconditions=set(),
        haltconditions=set()
    )

    assert test_nfa.start_state == test_state_start
    assert test_nfa.final_state == test_state_final


def test_valid_det_start_aloop_final():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_a = simple_state("a")

    test_nfa = BoboNFA(
        name="test_nfa_name",
        states={
            test_state_start.name: test_state_start,
            test_state_final.name: test_state_final,
            test_state_a.name: test_state_a
        },
        transitions={
            test_state_start.name: simple_transition(test_state_a.name),
            test_state_a.name: BoboTransition(
                state_names={
                    test_state_a.name,
                    test_state_final.name
                },
                strict=False
            ),
        },
        start_state_name=test_state_start.name,
        final_state_name=test_state_final.name,
        preconditions=set(),
        haltconditions=set()
    )

    assert test_nfa.start_state == test_state_start
    assert test_nfa.final_state == test_state_final


def test_valid_det_start_a_bloop_c_final():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_a = simple_state("a")
    test_state_b = simple_state("b")
    test_state_c = simple_state("c")

    test_nfa = BoboNFA(
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
                    test_state_b.name,
                    test_state_c.name
                },
                strict=False
            ),
            test_state_c.name: simple_transition(test_state_final.name)
        },
        start_state_name=test_state_start.name,
        final_state_name=test_state_final.name,
        preconditions=set(),
        haltconditions=set()
    )

    assert test_nfa.start_state == test_state_start
    assert test_nfa.final_state == test_state_final


def test_valid_det_start_a_bnegated_c_final():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_a = simple_state("a")
    test_state_b = simple_state("b", negated=True)
    test_state_c = simple_state("c")

    test_nfa = BoboNFA(
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
            test_state_b.name: simple_transition(test_state_c.name),
            test_state_c.name: simple_transition(test_state_final.name)
        },
        start_state_name=test_state_start.name,
        final_state_name=test_state_final.name,
        preconditions=set(),
        haltconditions=set()
    )

    assert test_nfa.start_state == test_state_start
    assert test_nfa.final_state == test_state_final


def test_valid_det_start_a_boptional_c_final():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_a = simple_state("a")
    test_state_b = simple_state("b", optional=True)
    test_state_c = simple_state("c")

    test_nfa = BoboNFA(
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
            test_state_b.name: simple_transition(test_state_c.name),
            test_state_c.name: simple_transition(test_state_final.name)
        },
        start_state_name=test_state_start.name,
        final_state_name=test_state_final.name,
        preconditions=set(),
        haltconditions=set()
    )

    assert test_nfa.start_state == test_state_start
    assert test_nfa.final_state == test_state_final
