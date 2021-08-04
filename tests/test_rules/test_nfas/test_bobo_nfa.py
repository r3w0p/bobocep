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


def _simple_state(
        state_id: str,
        group: str = None,
        negated: bool = False,
        optional: bool = False):
    return BoboState(
        name="test_state_name_{}".format(state_id),
        group="test_state_group_{}".format(
            group if group is not None else state_id),
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        negated=negated,
        optional=optional
    )


def _simple_transition(state_name: str, strict: bool = False):
    return BoboTransition(
        state_names={state_name},
        strict=strict
    )


def test_nfa_valid_det_start_final_only():
    test_state_start = _simple_state("start")
    test_state_final = _simple_state("final")

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_start.name: test_state_start,
        test_state_final.name: test_state_final
    }
    test_nfa_transitions = {
        test_state_start.name: _simple_transition(test_state_final.name)
    }
    test_start_state_name = test_state_start.name
    test_final_state_name = test_state_final.name
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
    assert test_nfa.start_state == test_state_start
    assert test_nfa.final_state == test_state_final
    assert test_nfa.preconditions == test_preconditions
    assert test_nfa.haltconditions == test_haltconditions


def test_nfa_valid_det_three_states():
    test_state_start = _simple_state("start")
    test_state_final = _simple_state("final")
    test_state_a = _simple_state("a")

    test_nfa = BoboNFA(
        name="test_nfa_name",
        states={
            test_state_start.name: test_state_start,
            test_state_final.name: test_state_final,
            test_state_a.name: test_state_a
        },
        transitions={
            test_state_start.name: _simple_transition(test_state_a.name),
            test_state_a.name: _simple_transition(test_state_final.name)
        },
        start_state_name=test_state_start.name,
        final_state_name=test_state_final.name,
        preconditions=[],
        haltconditions=[]
    )

    assert test_nfa.start_state == test_state_start
    assert test_nfa.final_state == test_state_final


def test_nfa_valid_det_five_states():
    test_state_start = _simple_state("start")
    test_state_final = _simple_state("final")
    test_state_a = _simple_state("a")
    test_state_b = _simple_state("b")
    test_state_c = _simple_state("c")

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
            test_state_start.name: _simple_transition(test_state_a.name),
            test_state_a.name: _simple_transition(test_state_b.name),
            test_state_b.name: _simple_transition(test_state_c.name),
            test_state_c.name: _simple_transition(test_state_final.name)
        },
        start_state_name=test_state_start.name,
        final_state_name=test_state_final.name,
        preconditions=[],
        haltconditions=[]
    )

    assert test_nfa.start_state == test_state_start
    assert test_nfa.final_state == test_state_final


def test_nfa_valid_nondet_start_a_group_final():
    test_state_start = _simple_state("start")
    test_state_final = _simple_state("final")
    test_state_a = _simple_state("a")
    test_state_b_1 = _simple_state("b", group="1")
    test_state_c_1 = _simple_state("c", group="1")

    test_nfa = BoboNFA(
        name="test_nfa_name",
        states={
            test_state_start.name: test_state_start,
            test_state_final.name: test_state_final,
            test_state_a.name: test_state_a,
            test_state_b_1.name: test_state_b_1,
            test_state_c_1.name: test_state_c_1
        },
        transitions={
            test_state_start.name: _simple_transition(test_state_a.name),
            test_state_a.name: BoboTransition(
                state_names={
                    test_state_b_1.name,
                    test_state_c_1.name
                },
                strict=False
            ),
            test_state_b_1.name: _simple_transition(test_state_final.name),
            test_state_c_1.name: _simple_transition(test_state_final.name)
        },
        start_state_name=test_state_start.name,
        final_state_name=test_state_final.name,
        preconditions=[],
        haltconditions=[]
    )

    assert test_nfa.start_state == test_state_start
    assert test_nfa.final_state == test_state_final


def test_nfa_valid_nondet_start_a_group_d_group_h_final():
    test_state_start = _simple_state("start")
    test_state_final = _simple_state("final")
    test_state_a = _simple_state("a")
    test_state_b_1 = _simple_state("b", group="1")
    test_state_c_1 = _simple_state("c", group="1")
    test_state_d = _simple_state("d")
    test_state_e_2 = _simple_state("e", group="2")
    test_state_f_2 = _simple_state("f", group="2")
    test_state_g_2 = _simple_state("g", group="2")
    test_state_h = _simple_state("h")

    test_nfa = BoboNFA(
        name="test_nfa_name",
        states={
            test_state_start.name: test_state_start,
            test_state_final.name: test_state_final,
            test_state_a.name: test_state_a,
            test_state_b_1.name: test_state_b_1,
            test_state_c_1.name: test_state_c_1,
            test_state_d.name: test_state_d,
            test_state_e_2.name: test_state_e_2,
            test_state_f_2.name: test_state_f_2,
            test_state_g_2.name: test_state_g_2,
            test_state_h.name: test_state_h
        },
        transitions={
            test_state_start.name: _simple_transition(test_state_a.name),
            test_state_a.name: BoboTransition(
                state_names={
                    test_state_b_1.name,
                    test_state_c_1.name
                },
                strict=False
            ),
            test_state_b_1.name: _simple_transition(test_state_d.name),
            test_state_c_1.name: _simple_transition(test_state_d.name),
            test_state_d.name: BoboTransition(
                state_names={
                    test_state_e_2.name,
                    test_state_f_2.name,
                    test_state_g_2.name
                },
                strict=False
            ),
            test_state_e_2.name: _simple_transition(test_state_h.name),
            test_state_f_2.name: _simple_transition(test_state_h.name),
            test_state_g_2.name: _simple_transition(test_state_h.name),
            test_state_h.name: _simple_transition(test_state_final.name)
        },
        start_state_name=test_state_start.name,
        final_state_name=test_state_final.name,
        preconditions=[],
        haltconditions=[]
    )

    assert test_nfa.start_state == test_state_start
    assert test_nfa.final_state == test_state_final


def test_nfa_valid_nondet_start_a_group_group_h_final():
    test_state_start = _simple_state("start")
    test_state_final = _simple_state("final")
    test_state_a = _simple_state("a")
    test_state_b_1 = _simple_state("b", group="1")
    test_state_c_1 = _simple_state("c", group="1")
    test_state_d_1 = _simple_state("d", group="1")
    test_state_e_2 = _simple_state("e", group="2")
    test_state_f_2 = _simple_state("f", group="2")
    test_state_g_2 = _simple_state("g", group="2")
    test_state_h = _simple_state("h")

    state_names_1 = {
        test_state_b_1.name,
        test_state_c_1.name,
        test_state_d_1.name
    }

    state_names_2 = {
        test_state_e_2.name,
        test_state_f_2.name,
        test_state_g_2.name
    }

    test_nfa = BoboNFA(
        name="test_nfa_name",
        states={
            test_state_start.name: test_state_start,
            test_state_final.name: test_state_final,
            test_state_a.name: test_state_a,
            test_state_b_1.name: test_state_b_1,
            test_state_c_1.name: test_state_c_1,
            test_state_d_1.name: test_state_d_1,
            test_state_e_2.name: test_state_e_2,
            test_state_f_2.name: test_state_f_2,
            test_state_g_2.name: test_state_g_2,
            test_state_h.name: test_state_h
        },
        transitions={
            test_state_start.name: _simple_transition(test_state_a.name),
            test_state_a.name: BoboTransition(
                state_names=state_names_1,
                strict=False
            ),
            test_state_b_1.name: BoboTransition(
                state_names=state_names_2,
                strict=False
            ),
            test_state_c_1.name: BoboTransition(
                state_names=state_names_2,
                strict=False
            ),
            test_state_d_1.name: BoboTransition(
                state_names=state_names_2,
                strict=False
            ),
            test_state_e_2.name: _simple_transition(test_state_h.name),
            test_state_f_2.name: _simple_transition(test_state_h.name),
            test_state_g_2.name: _simple_transition(test_state_h.name),
            test_state_h.name: _simple_transition(test_state_final.name)
        },
        start_state_name=test_state_start.name,
        final_state_name=test_state_final.name,
        preconditions=[],
        haltconditions=[]
    )

    assert test_nfa.start_state == test_state_start
    assert test_nfa.final_state == test_state_final


def test_nfa_valid_det_self_loop_three_states():
    test_state_start = _simple_state("start")
    test_state_final = _simple_state("final")
    test_state_a = _simple_state("a")

    test_nfa = BoboNFA(
        name="test_nfa_name",
        states={
            test_state_start.name: test_state_start,
            test_state_final.name: test_state_final,
            test_state_a.name: test_state_a
        },
        transitions={
            test_state_start.name: _simple_transition(test_state_a.name),
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
        preconditions=[],
        haltconditions=[]
    )

    assert test_nfa.start_state == test_state_start
    assert test_nfa.final_state == test_state_final


def test_nfa_valid_det_self_loop_five_states():
    test_state_start = _simple_state("start")
    test_state_final = _simple_state("final")
    test_state_a = _simple_state("a")
    test_state_b = _simple_state("b")
    test_state_c = _simple_state("c")

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
            test_state_start.name: _simple_transition(test_state_a.name),
            test_state_a.name: _simple_transition(test_state_b.name),
            test_state_b.name: BoboTransition(
                state_names={
                    test_state_b.name,
                    test_state_c.name
                },
                strict=False
            ),
            test_state_c.name: _simple_transition(test_state_final.name)
        },
        start_state_name=test_state_start.name,
        final_state_name=test_state_final.name,
        preconditions=[],
        haltconditions=[]
    )

    assert test_nfa.start_state == test_state_start
    assert test_nfa.final_state == test_state_final


def test_nfa_invalid_det_self_loop_only():
    test_state_start = _simple_state("start")
    test_state_final = _simple_state("final")
    test_state_a = _simple_state("a")

    with pytest.raises(PreconditionError):
        BoboNFA(
            name="test_nfa_name",
            states={
                test_state_start.name: test_state_start,
                test_state_final.name: test_state_final,
                test_state_a.name: test_state_a
            },
            transitions={
                test_state_start.name: _simple_transition(test_state_a.name),
                test_state_a.name: BoboTransition(
                    state_names={
                        test_state_a.name
                    },
                    strict=False
                ),
            },
            start_state_name=test_state_start.name,
            final_state_name=test_state_final.name,
            preconditions=[],
            haltconditions=[]
        )


def test_nfa_invalid_one_state():
    test_state_one = _simple_state(state_id="one")

    with pytest.raises(PreconditionError):
        BoboNFA(
            name="test_nfa_name",
            states={test_state_one.name: test_state_one},
            transitions={},
            start_state_name=test_state_one.name,
            final_state_name=test_state_one.name,
            preconditions=[],
            haltconditions=[]
        )
