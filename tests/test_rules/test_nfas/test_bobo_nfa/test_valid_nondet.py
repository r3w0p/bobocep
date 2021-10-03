from bobocep.rules.nfas.bobo_nfa import BoboNFA
from tests.test_rules.test_nfas.test_bobo_nfa.helpers_bobo_nfa import *


def test_valid_nondet_start_a_2group_final():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_a = simple_state("a")
    test_state_b_1 = simple_state("b", group="1")
    test_state_c_1 = simple_state("c", group="1")

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
            test_state_start.name: simple_transition(test_state_a.name),
            test_state_a.name: BoboTransition(
                state_names={
                    test_state_b_1.name,
                    test_state_c_1.name
                },
                strict=False
            ),
            test_state_b_1.name: simple_transition(test_state_final.name),
            test_state_c_1.name: simple_transition(test_state_final.name)
        },
        start_state_name=test_state_start.name,
        final_state_name=test_state_final.name,
        preconditions=set(),
        haltconditions=set()
    )

    assert test_nfa.start_state == test_state_start
    assert test_nfa.final_state == test_state_final


def test_valid_nondet_start_a_2group_d_3group_h_final():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_a = simple_state("a")
    test_state_b_1 = simple_state("b", group="1")
    test_state_c_1 = simple_state("c", group="1")
    test_state_d = simple_state("d")
    test_state_e_2 = simple_state("e", group="2")
    test_state_f_2 = simple_state("f", group="2")
    test_state_g_2 = simple_state("g", group="2")
    test_state_h = simple_state("h")

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
            test_state_start.name: simple_transition(test_state_a.name),
            test_state_a.name: BoboTransition(
                state_names={
                    test_state_b_1.name,
                    test_state_c_1.name
                },
                strict=False
            ),
            test_state_b_1.name: simple_transition(test_state_d.name),
            test_state_c_1.name: simple_transition(test_state_d.name),
            test_state_d.name: BoboTransition(
                state_names={
                    test_state_e_2.name,
                    test_state_f_2.name,
                    test_state_g_2.name
                },
                strict=False
            ),
            test_state_e_2.name: simple_transition(test_state_h.name),
            test_state_f_2.name: simple_transition(test_state_h.name),
            test_state_g_2.name: simple_transition(test_state_h.name),
            test_state_h.name: simple_transition(test_state_final.name)
        },
        start_state_name=test_state_start.name,
        final_state_name=test_state_final.name,
        preconditions=set(),
        haltconditions=set()
    )

    assert test_nfa.start_state == test_state_start
    assert test_nfa.final_state == test_state_final


def test_valid_nondet_start_a_3group_3group_h_final():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_a = simple_state("a")
    test_state_b_1 = simple_state("b", group="1")
    test_state_c_1 = simple_state("c", group="1")
    test_state_d_1 = simple_state("d", group="1")
    test_state_e_2 = simple_state("e", group="2")
    test_state_f_2 = simple_state("f", group="2")
    test_state_g_2 = simple_state("g", group="2")
    test_state_h = simple_state("h")

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
            test_state_start.name: simple_transition(test_state_a.name),
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
            test_state_e_2.name: simple_transition(test_state_h.name),
            test_state_f_2.name: simple_transition(test_state_h.name),
            test_state_g_2.name: simple_transition(test_state_h.name),
            test_state_h.name: simple_transition(test_state_final.name)
        },
        start_state_name=test_state_start.name,
        final_state_name=test_state_final.name,
        preconditions=set(),
        haltconditions=set()
    )

    assert test_nfa.start_state == test_state_start
    assert test_nfa.final_state == test_state_final
