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

# todo nondet negated group: one in group and all
# todo nondet optional group: one in group and all
# todo penultimate nondet negated optional


def test_invalid_nondet_start_state_nondet_transitions():
    test_state_start = simple_state("start")
    test_state_final = simple_state("final")
    test_state_a = simple_state("a")
    test_state_b = simple_state("b")
    test_state_c = simple_state("c")

    test_nfa_name = "test_nfa_name"
    test_nfa_states = {
        test_state_start.name: test_state_start,
        test_state_final.name: test_state_final,
        test_state_a.name: test_state_a,
        test_state_b.name: test_state_b,
        test_state_c.name: test_state_c
    }
    test_nfa_transitions = {
        test_state_start.name: BoboTransition(
            state_names={
                test_state_a.name,
                test_state_b.name,
                test_state_c.name
            },
            strict=False
        ),
        test_state_a.name: simple_transition(test_state_final.name),
        test_state_b.name: simple_transition(test_state_final.name),
        test_state_c.name: simple_transition(test_state_final.name)
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