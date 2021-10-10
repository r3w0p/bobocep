import pytest
from dpcontracts import PreconditionError

from bobocep.rules.nfas.bobo_nfa import BoboNFA
from tests.test_rules.test_nfas.test_bobo_nfa.helpers_bobo_nfa import *
from bobocep.rules.nfas.bobo_pattern import BoboPattern
from bobocep.rules.predicates.bobo_predicate_true import BoboPredicateTrue


def test_valid_det_start_only_times1():
    test_pattern_name = "test_pattern_name"
    test_pattern = BoboPattern(name=test_pattern_name)

    test_start_group = "test_group_start"
    test_start_predicate = BoboPredicateTrue()
    test_start_times = 1

    test_pattern.start(
        group=test_start_group,
        predicate=test_start_predicate,
        times=test_start_times)

    test_nfa = test_pattern.generate_nfa()

    assert test_nfa.name == test_pattern_name

    assert len(test_nfa.states.keys()) == 1
    assert len(test_nfa.transitions.keys()) == 0

    assert test_nfa.start_state is not None
    assert test_nfa.final_state is not None
    assert test_nfa.start_state == test_nfa.final_state

    assert test_nfa.preconditions == set()
    assert test_nfa.haltconditions == set()
