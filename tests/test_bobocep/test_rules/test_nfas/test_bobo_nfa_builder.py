import unittest
from typing import List

from bobocep.rules.bobo_rule_builder import BoboRuleBuilder
from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.nfas.patterns.bobo_pattern import BoboPattern
from bobocep.rules.predicates.bobo_predicate_function import \
    BoboPredicateFunction

STATE_A = "state_a"
STATE_B = "state_b"
STATE_C = "state_c"
STATE_D = "state_d"

LABEL_LAYER_A = "LABEL_LAYER_A"
LABEL_LAYER_B = "LABEL_LAYER_B"
LABEL_LAYER_C = "LABEL_LAYER_C"
LABEL_LAYER_D = "LABEL_LAYER_D"

NFA_NAME_A = "NFA_NAME_A"


def predicate_key_a_value_a(event: BoboEvent,
                            history: BoboHistory,
                            recents: List[CompositeEvent]):
    return event.data == 1


def predicate_key_a_value_b(event: BoboEvent,
                            history: BoboHistory,
                            recents: List[CompositeEvent]):
    return event.data == 2


def predicate_key_a_value_c(event: BoboEvent,
                            history: BoboHistory,
                            recents: List[CompositeEvent]):
    return event.data == 3


def predicate_key_a_value_d(event: BoboEvent,
                            history: BoboHistory,
                            recents: List[CompositeEvent]):
    return event.data == 4


class TestBoboNFABuilder(unittest.TestCase):

    def test_invalid_empty_pattern(self):
        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.nfa(NFA_NAME_A, BoboPattern())

    def test_invalid_first_state_is_loop(self):
        predicate_a = BoboPredicateFunction(predicate_key_a_value_a)
        predicate_b = BoboPredicateFunction(predicate_key_a_value_b)

        pattern = BoboPattern() \
            .followed_by(LABEL_LAYER_A, predicate_a, loop=True) \
            .followed_by(LABEL_LAYER_B, predicate_b)

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.nfa(NFA_NAME_A, pattern)

    def test_invalid_first_state_is_negated(self):
        predicate_a = BoboPredicateFunction(predicate_key_a_value_a)
        predicate_b = BoboPredicateFunction(predicate_key_a_value_b)

        pattern = BoboPattern() \
            .not_followed_by(LABEL_LAYER_A, predicate_a) \
            .followed_by(LABEL_LAYER_B, predicate_b)

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.nfa(NFA_NAME_A, pattern)

    def test_invalid_first_state_is_optional(self):
        predicate_a = BoboPredicateFunction(predicate_key_a_value_a)
        predicate_b = BoboPredicateFunction(predicate_key_a_value_b)

        pattern = BoboPattern() \
            .followed_by(LABEL_LAYER_A, predicate_a, optional=True) \
            .followed_by(LABEL_LAYER_B, predicate_b)

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.nfa(NFA_NAME_A, pattern)

    def test_invalid_first_states_are_nondeterministic(self):
        predicate_a = BoboPredicateFunction(predicate_key_a_value_a)
        predicate_b = BoboPredicateFunction(predicate_key_a_value_b)
        predicate_c = BoboPredicateFunction(predicate_key_a_value_c)

        pattern = BoboPattern() \
            .followed_by_any(LABEL_LAYER_A, [predicate_a, predicate_b]) \
            .followed_by(LABEL_LAYER_B, predicate_c)

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.nfa(NFA_NAME_A, pattern)

    def test_invalid_accepting_states_are_nondeterministic(self):
        predicate_a = BoboPredicateFunction(predicate_key_a_value_a)
        predicate_b = BoboPredicateFunction(predicate_key_a_value_b)
        predicate_c = BoboPredicateFunction(predicate_key_a_value_c)

        pattern = BoboPattern() \
            .followed_by(LABEL_LAYER_A, predicate_a) \
            .followed_by_any(LABEL_LAYER_B, [predicate_b, predicate_c])

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.nfa(NFA_NAME_A, pattern)

    def test_invalid_duplicate_labels(self):
        predicate_a = BoboPredicateFunction(predicate_key_a_value_a)
        predicate_b = BoboPredicateFunction(predicate_key_a_value_b)

        pattern = BoboPattern() \
            .followed_by(LABEL_LAYER_A, predicate_a) \
            .followed_by(LABEL_LAYER_A, predicate_b)

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.nfa(NFA_NAME_A, pattern)

    def test_generate_nfa_deterministic_append_patterns(self):
        predicate_a = BoboPredicateFunction(predicate_key_a_value_a)
        predicate_b = BoboPredicateFunction(predicate_key_a_value_b)
        predicate_c = BoboPredicateFunction(predicate_key_a_value_c)
        predicate_d = BoboPredicateFunction(predicate_key_a_value_d)

        pattern_1 = BoboPattern() \
            .followed_by(LABEL_LAYER_A, predicate_a) \
            .next(LABEL_LAYER_B, predicate_b)

        pattern_2 = BoboPattern() \
            .next(LABEL_LAYER_C, predicate_c)

        pattern_3 = BoboPattern() \
            .followed_by(LABEL_LAYER_D, predicate_d)

        pattern_1.append([pattern_2, pattern_3])

        nfa = BoboRuleBuilder.nfa(NFA_NAME_A, pattern_1)

        state_name_a = "{}-{}-{}".format(LABEL_LAYER_A, 1, 1)
        state_name_b = "{}-{}-{}".format(LABEL_LAYER_B, 1, 1)
        state_name_c = "{}-{}-{}".format(LABEL_LAYER_C, 1, 1)
        state_name_d = "{}-{}-{}".format(LABEL_LAYER_D, 1, 1)

        # variables
        self.assertEqual(nfa.name, NFA_NAME_A)
        self.assertEqual(4, len(nfa.states))
        self.assertEqual(4, len(nfa.transitions))
        self.assertEqual(state_name_a, nfa.start_state.name)
        self.assertEqual(state_name_d, nfa.accepting_state.name)
        self.assertEqual(0, len(nfa.preconditions))

        # states
        self.assertTrue(state_name_a in nfa.states)
        self.assertTrue(state_name_b in nfa.states)
        self.assertTrue(state_name_c in nfa.states)
        self.assertTrue(state_name_d in nfa.states)

        self.assertEqual(state_name_a, nfa.states[state_name_a].name)
        self.assertEqual(state_name_b, nfa.states[state_name_b].name)
        self.assertEqual(state_name_c, nfa.states[state_name_c].name)
        self.assertEqual(state_name_d, nfa.states[state_name_d].name)

        self.assertEqual(LABEL_LAYER_A, nfa.states[state_name_a].label)
        self.assertEqual(LABEL_LAYER_B, nfa.states[state_name_b].label)
        self.assertEqual(LABEL_LAYER_C, nfa.states[state_name_c].label)
        self.assertEqual(LABEL_LAYER_D, nfa.states[state_name_d].label)

        self.assertFalse(nfa.states[state_name_a].is_negated)
        self.assertFalse(nfa.states[state_name_b].is_negated)
        self.assertFalse(nfa.states[state_name_c].is_negated)
        self.assertFalse(nfa.states[state_name_d].is_negated)

        self.assertFalse(nfa.states[state_name_a].is_optional)
        self.assertFalse(nfa.states[state_name_b].is_optional)
        self.assertFalse(nfa.states[state_name_c].is_optional)
        self.assertFalse(nfa.states[state_name_d].is_optional)

        # transitions
        self.assertTrue(state_name_a in nfa.transitions)
        self.assertTrue(state_name_b in nfa.transitions)
        self.assertTrue(state_name_c in nfa.transitions)
        self.assertTrue(state_name_d in nfa.transitions)

        self.assertListEqual([state_name_b],
                             nfa.transitions[state_name_a].state_names)
        self.assertListEqual([state_name_c],
                             nfa.transitions[state_name_b].state_names)
        self.assertListEqual([state_name_d],
                             nfa.transitions[state_name_c].state_names)
        self.assertListEqual([], nfa.transitions[state_name_d].state_names)

        self.assertTrue(nfa.transitions[state_name_a].is_strict)
        self.assertTrue(nfa.transitions[state_name_b].is_strict)
        self.assertFalse(nfa.transitions[state_name_c].is_strict)
        self.assertFalse(nfa.transitions[state_name_d].is_strict)

    def test_generate_nfa_deterministic_all_relaxed(self):
        predicate_a = BoboPredicateFunction(predicate_key_a_value_a)
        predicate_b = BoboPredicateFunction(predicate_key_a_value_b)
        predicate_c = BoboPredicateFunction(predicate_key_a_value_c)

        pattern = BoboPattern() \
            .followed_by(LABEL_LAYER_A, predicate_a) \
            .followed_by(LABEL_LAYER_B, predicate_b) \
            .followed_by(LABEL_LAYER_C, predicate_c)

        nfa = BoboRuleBuilder.nfa(NFA_NAME_A, pattern)

        state_name_a = "{}-{}-{}".format(LABEL_LAYER_A, 1, 1)
        state_name_b = "{}-{}-{}".format(LABEL_LAYER_B, 1, 1)
        state_name_c = "{}-{}-{}".format(LABEL_LAYER_C, 1, 1)

        # variables
        self.assertEqual(nfa.name, NFA_NAME_A)
        self.assertEqual(3, len(nfa.states))
        self.assertEqual(3, len(nfa.transitions))
        self.assertEqual(state_name_a, nfa.start_state.name)
        self.assertEqual(state_name_c, nfa.accepting_state.name)
        self.assertEqual(0, len(nfa.preconditions))

        # states
        self.assertTrue(state_name_a in nfa.states)
        self.assertTrue(state_name_b in nfa.states)
        self.assertTrue(state_name_c in nfa.states)

        self.assertEqual(state_name_a, nfa.states[state_name_a].name)
        self.assertEqual(state_name_b, nfa.states[state_name_b].name)
        self.assertEqual(state_name_c, nfa.states[state_name_c].name)

        self.assertEqual(LABEL_LAYER_A, nfa.states[state_name_a].label)
        self.assertEqual(LABEL_LAYER_B, nfa.states[state_name_b].label)
        self.assertEqual(LABEL_LAYER_C, nfa.states[state_name_c].label)

        self.assertFalse(nfa.states[state_name_a].is_negated)
        self.assertFalse(nfa.states[state_name_b].is_negated)
        self.assertFalse(nfa.states[state_name_c].is_negated)

        self.assertFalse(nfa.states[state_name_a].is_optional)
        self.assertFalse(nfa.states[state_name_b].is_optional)
        self.assertFalse(nfa.states[state_name_c].is_optional)

        # transitions
        self.assertTrue(state_name_a in nfa.transitions)
        self.assertTrue(state_name_b in nfa.transitions)
        self.assertTrue(state_name_c in nfa.transitions)

        self.assertListEqual([state_name_b],
                             nfa.transitions[state_name_a].state_names)
        self.assertListEqual([state_name_c],
                             nfa.transitions[state_name_b].state_names)
        self.assertListEqual([], nfa.transitions[state_name_c].state_names)

        self.assertFalse(nfa.transitions[state_name_a].is_strict)
        self.assertFalse(nfa.transitions[state_name_b].is_strict)
        self.assertFalse(nfa.transitions[state_name_c].is_strict)

    def test_generate_nfa_deterministic_all_strict(self):
        predicate_a = BoboPredicateFunction(predicate_key_a_value_a)
        predicate_b = BoboPredicateFunction(predicate_key_a_value_b)
        predicate_c = BoboPredicateFunction(predicate_key_a_value_c)

        pattern = BoboPattern() \
            .next(LABEL_LAYER_A, predicate_a) \
            .next(LABEL_LAYER_B, predicate_b) \
            .next(LABEL_LAYER_C, predicate_c)

        nfa = BoboRuleBuilder.nfa(NFA_NAME_A, pattern)

        state_name_a = "{}-{}-{}".format(LABEL_LAYER_A, 1, 1)
        state_name_b = "{}-{}-{}".format(LABEL_LAYER_B, 1, 1)
        state_name_c = "{}-{}-{}".format(LABEL_LAYER_C, 1, 1)

        # variables
        self.assertEqual(nfa.name, NFA_NAME_A)
        self.assertEqual(3, len(nfa.states))
        self.assertEqual(3, len(nfa.transitions))
        self.assertEqual(state_name_a, nfa.start_state.name)
        self.assertEqual(state_name_c, nfa.accepting_state.name)
        self.assertEqual(0, len(nfa.preconditions))

        # states
        self.assertTrue(state_name_a in nfa.states)
        self.assertTrue(state_name_b in nfa.states)
        self.assertTrue(state_name_c in nfa.states)

        self.assertEqual(state_name_a, nfa.states[state_name_a].name)
        self.assertEqual(state_name_b, nfa.states[state_name_b].name)
        self.assertEqual(state_name_c, nfa.states[state_name_c].name)

        self.assertEqual(LABEL_LAYER_A, nfa.states[state_name_a].label)
        self.assertEqual(LABEL_LAYER_B, nfa.states[state_name_b].label)
        self.assertEqual(LABEL_LAYER_C, nfa.states[state_name_c].label)

        self.assertFalse(nfa.states[state_name_a].is_negated)
        self.assertFalse(nfa.states[state_name_b].is_negated)
        self.assertFalse(nfa.states[state_name_c].is_negated)

        self.assertFalse(nfa.states[state_name_a].is_optional)
        self.assertFalse(nfa.states[state_name_b].is_optional)
        self.assertFalse(nfa.states[state_name_c].is_optional)

        # transitions
        self.assertTrue(state_name_a in nfa.transitions)
        self.assertTrue(state_name_b in nfa.transitions)
        self.assertTrue(state_name_c in nfa.transitions)

        self.assertListEqual([state_name_b],
                             nfa.transitions[state_name_a].state_names)
        self.assertListEqual([state_name_c],
                             nfa.transitions[state_name_b].state_names)
        self.assertListEqual([], nfa.transitions[state_name_c].state_names)

        self.assertTrue(nfa.transitions[state_name_a].is_strict)
        self.assertTrue(nfa.transitions[state_name_b].is_strict)
        self.assertFalse(nfa.transitions[state_name_c].is_strict)

    def test_generate_nfa_deterministic_negated(self):
        predicate_a = BoboPredicateFunction(predicate_key_a_value_a)
        predicate_b = BoboPredicateFunction(predicate_key_a_value_b)
        predicate_c = BoboPredicateFunction(predicate_key_a_value_c)

        pattern = BoboPattern() \
            .followed_by(LABEL_LAYER_A, predicate_a) \
            .not_followed_by(LABEL_LAYER_B, predicate_b) \
            .followed_by(LABEL_LAYER_C, predicate_c)

        nfa = BoboRuleBuilder.nfa(NFA_NAME_A, pattern)

        state_name_a = "{}-{}-{}".format(LABEL_LAYER_A, 1, 1)
        state_name_b = "{}-{}-{}".format(LABEL_LAYER_B, 1, 1)
        state_name_c = "{}-{}-{}".format(LABEL_LAYER_C, 1, 1)

        # variables
        self.assertEqual(nfa.name, NFA_NAME_A)
        self.assertEqual(3, len(nfa.states))
        self.assertEqual(3, len(nfa.transitions))
        self.assertEqual(state_name_a, nfa.start_state.name)
        self.assertEqual(state_name_c, nfa.accepting_state.name)
        self.assertEqual(0, len(nfa.preconditions))

        # states
        self.assertTrue(state_name_a in nfa.states)
        self.assertTrue(state_name_b in nfa.states)
        self.assertTrue(state_name_c in nfa.states)

        self.assertEqual(state_name_a, nfa.states[state_name_a].name)
        self.assertEqual(state_name_b, nfa.states[state_name_b].name)
        self.assertEqual(state_name_c, nfa.states[state_name_c].name)

        self.assertEqual(LABEL_LAYER_A, nfa.states[state_name_a].label)
        self.assertEqual(LABEL_LAYER_B, nfa.states[state_name_b].label)
        self.assertEqual(LABEL_LAYER_C, nfa.states[state_name_c].label)

        self.assertFalse(nfa.states[state_name_a].is_negated)
        self.assertTrue(nfa.states[state_name_b].is_negated)
        self.assertFalse(nfa.states[state_name_c].is_negated)

        self.assertFalse(nfa.states[state_name_a].is_optional)
        self.assertFalse(nfa.states[state_name_b].is_optional)
        self.assertFalse(nfa.states[state_name_c].is_optional)

        # transitions
        self.assertTrue(state_name_a in nfa.transitions)
        self.assertTrue(state_name_b in nfa.transitions)
        self.assertTrue(state_name_c in nfa.transitions)

        self.assertListEqual([state_name_b],
                             nfa.transitions[state_name_a].state_names)
        self.assertListEqual([state_name_c],
                             nfa.transitions[state_name_b].state_names)
        self.assertListEqual([], nfa.transitions[state_name_c].state_names)

        self.assertFalse(nfa.transitions[state_name_a].is_strict)
        self.assertFalse(nfa.transitions[state_name_b].is_strict)
        self.assertFalse(nfa.transitions[state_name_c].is_strict)

    def test_generate_nfa_nondeterministic_all_relaxed(self):
        predicate_a = BoboPredicateFunction(predicate_key_a_value_a)
        predicate_b1 = BoboPredicateFunction(predicate_key_a_value_b)
        predicate_b2 = BoboPredicateFunction(predicate_key_a_value_c)
        predicate_c = BoboPredicateFunction(predicate_key_a_value_d)

        pattern = BoboPattern() \
            .followed_by(LABEL_LAYER_A, predicate_a) \
            .followed_by_any(LABEL_LAYER_B, [predicate_b1, predicate_b2]) \
            .followed_by(LABEL_LAYER_C, predicate_c)

        nfa = BoboRuleBuilder.nfa(NFA_NAME_A, pattern)

        state_name_a = "{}-{}-{}".format(LABEL_LAYER_A, 1, 1)
        state_name_b1 = "{}-{}-{}".format(LABEL_LAYER_B, 1, 1)
        state_name_b2 = "{}-{}-{}".format(LABEL_LAYER_B, 2, 1)
        state_name_c = "{}-{}-{}".format(LABEL_LAYER_C, 1, 1)

        # variables
        self.assertEqual(nfa.name, NFA_NAME_A)
        self.assertEqual(4, len(nfa.states))
        self.assertEqual(4, len(nfa.transitions))
        self.assertEqual(state_name_a, nfa.start_state.name)
        self.assertEqual(state_name_c, nfa.accepting_state.name)
        self.assertEqual(0, len(nfa.preconditions))

        # states
        self.assertTrue(state_name_a in nfa.states)
        self.assertTrue(state_name_b1 in nfa.states)
        self.assertTrue(state_name_b2 in nfa.states)
        self.assertTrue(state_name_c in nfa.states)

        self.assertEqual(state_name_a, nfa.states[state_name_a].name)
        self.assertEqual(state_name_b1, nfa.states[state_name_b1].name)
        self.assertEqual(state_name_b2, nfa.states[state_name_b2].name)
        self.assertEqual(state_name_c, nfa.states[state_name_c].name)

        self.assertEqual(LABEL_LAYER_A, nfa.states[state_name_a].label)
        self.assertEqual(LABEL_LAYER_B, nfa.states[state_name_b1].label)
        self.assertEqual(LABEL_LAYER_B, nfa.states[state_name_b2].label)
        self.assertEqual(LABEL_LAYER_C, nfa.states[state_name_c].label)

        self.assertFalse(nfa.states[state_name_a].is_negated)
        self.assertFalse(nfa.states[state_name_b1].is_negated)
        self.assertFalse(nfa.states[state_name_b2].is_negated)
        self.assertFalse(nfa.states[state_name_c].is_negated)

        self.assertFalse(nfa.states[state_name_a].is_optional)
        self.assertFalse(nfa.states[state_name_b1].is_optional)
        self.assertFalse(nfa.states[state_name_b2].is_optional)
        self.assertFalse(nfa.states[state_name_c].is_optional)

        # transitions
        self.assertTrue(state_name_a in nfa.transitions)
        self.assertTrue(state_name_b1 in nfa.transitions)
        self.assertTrue(state_name_b2 in nfa.transitions)
        self.assertTrue(state_name_c in nfa.transitions)

        self.assertListEqual([state_name_b1, state_name_b2],
                             nfa.transitions[state_name_a].state_names)
        self.assertListEqual([state_name_c],
                             nfa.transitions[state_name_b1].state_names)
        self.assertListEqual([state_name_c],
                             nfa.transitions[state_name_b2].state_names)
        self.assertListEqual([], nfa.transitions[state_name_c].state_names)

        self.assertFalse(nfa.transitions[state_name_a].is_strict)
        self.assertFalse(nfa.transitions[state_name_b1].is_strict)
        self.assertFalse(nfa.transitions[state_name_b2].is_strict)
        self.assertFalse(nfa.transitions[state_name_c].is_strict)

    def test_generate_nfa_times(self):
        predicate_a = BoboPredicateFunction(predicate_key_a_value_a)

        pattern = BoboPattern() \
            .followed_by(LABEL_LAYER_A, predicate_a, times=5)

        nfa = BoboRuleBuilder.nfa(NFA_NAME_A, pattern)

        state_name_a1 = "{}-{}-{}".format(LABEL_LAYER_A, 1, 1)
        state_name_a2 = "{}-{}-{}".format(LABEL_LAYER_A, 1, 2)
        state_name_a3 = "{}-{}-{}".format(LABEL_LAYER_A, 1, 3)
        state_name_a4 = "{}-{}-{}".format(LABEL_LAYER_A, 1, 4)
        state_name_a5 = "{}-{}-{}".format(LABEL_LAYER_A, 1, 5)

        # variables
        self.assertEqual(5, len(nfa.states))
        self.assertEqual(5, len(nfa.transitions))
        self.assertEqual(state_name_a1, nfa.start_state.name)
        self.assertEqual(state_name_a5, nfa.accepting_state.name)

        # states
        self.assertEqual(state_name_a1, nfa.states[state_name_a1].name)
        self.assertEqual(state_name_a2, nfa.states[state_name_a2].name)
        self.assertEqual(state_name_a3, nfa.states[state_name_a3].name)
        self.assertEqual(state_name_a4, nfa.states[state_name_a4].name)
        self.assertEqual(state_name_a5, nfa.states[state_name_a5].name)

        self.assertEqual(LABEL_LAYER_A, nfa.states[state_name_a1].label)
        self.assertEqual(LABEL_LAYER_A, nfa.states[state_name_a2].label)
        self.assertEqual(LABEL_LAYER_A, nfa.states[state_name_a3].label)
        self.assertEqual(LABEL_LAYER_A, nfa.states[state_name_a4].label)
        self.assertEqual(LABEL_LAYER_A, nfa.states[state_name_a5].label)

        # transitions
        self.assertListEqual([state_name_a2],
                             nfa.transitions[state_name_a1].state_names)
        self.assertListEqual([state_name_a3],
                             nfa.transitions[state_name_a2].state_names)
        self.assertListEqual([state_name_a4],
                             nfa.transitions[state_name_a3].state_names)
        self.assertListEqual([state_name_a5],
                             nfa.transitions[state_name_a4].state_names)
        self.assertListEqual([], nfa.transitions[state_name_a5].state_names)

    def test_generate_nfa_loop(self):
        predicate_a = BoboPredicateFunction(predicate_key_a_value_a)
        predicate_b = BoboPredicateFunction(predicate_key_a_value_b)
        predicate_c = BoboPredicateFunction(predicate_key_a_value_c)

        pattern = BoboPattern() \
            .followed_by(LABEL_LAYER_A, predicate_a) \
            .followed_by(LABEL_LAYER_B, predicate_b, loop=True) \
            .followed_by(LABEL_LAYER_C, predicate_c)

        nfa = BoboRuleBuilder.nfa(NFA_NAME_A, pattern)

        state_name_a = "{}-{}-{}".format(LABEL_LAYER_A, 1, 1)
        state_name_b = "{}-{}-{}".format(LABEL_LAYER_B, 1, 1)
        state_name_c = "{}-{}-{}".format(LABEL_LAYER_C, 1, 1)

        # variables
        self.assertEqual(3, len(nfa.states))
        self.assertEqual(3, len(nfa.transitions))
        self.assertEqual(state_name_a, nfa.start_state.name)
        self.assertEqual(state_name_c, nfa.accepting_state.name)

        # states
        self.assertEqual(state_name_a, nfa.states[state_name_a].name)
        self.assertEqual(state_name_b, nfa.states[state_name_b].name)
        self.assertEqual(state_name_c, nfa.states[state_name_c].name)

        self.assertEqual(LABEL_LAYER_A, nfa.states[state_name_a].label)
        self.assertEqual(LABEL_LAYER_B, nfa.states[state_name_b].label)
        self.assertEqual(LABEL_LAYER_C, nfa.states[state_name_c].label)

        # transitions
        self.assertListEqual([state_name_b],
                             nfa.transitions[state_name_a].state_names)
        self.assertEqual({state_name_b, state_name_c},
                         set(nfa.transitions[state_name_b].state_names))
        self.assertListEqual([], nfa.transitions[state_name_c].state_names)
