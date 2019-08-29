import unittest

from bobocep.rules.transitions.bobo_transition import BoboTransition

STATE_A = "state_a"
STATE_B = "state_b"
STATE_C = "state_c"


class TestBoboTransition(unittest.TestCase):

    def test_invalid_nondeterminism_with_strict_contiguity(self):
        state_names = [STATE_A, STATE_B, STATE_C]

        with self.assertRaises(RuntimeError):
            BoboTransition(state_names=state_names,
                           strict=True)

    def test_to_dict(self):
        state_names = [STATE_A, STATE_B, STATE_C]
        strict = False

        transition = BoboTransition(state_names=state_names,
                                    strict=strict)

        self.assertDictEqual(transition.to_dict(), {
            BoboTransition.STATE_NAMES: transition.state_names,
            BoboTransition.STRICT: transition.is_strict
        })
