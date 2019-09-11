import unittest

from bobocep.receiver.validators.str_dict_validator import StrDictValidator
from bobocep.rules.nfas.patterns.bobo_pattern import BoboPattern
from bobocep.rules.predicates.bobo_predicate_callable import \
    BoboPredicateCallable
from bobocep.setup.bobo_complex_event import BoboComplexEvent
from bobocep.setup.bobo_setup import BoboSetup

NAME_DEF_A = "name_def_a"

LABEL_A = "label_a"
LABEL_B = "label_b"
LABEL_C = "label_c"
LABEL_D = "label_d"

KEY_A = "key_a"
VALUE_A = "value_a"
DATA_DICT_A = {KEY_A: VALUE_A}

stub_predicate_true = BoboPredicateCallable(lambda e, h, r: True)

stub_pattern_1 = BoboPattern().followed_by(
    label=LABEL_A,
    predicate=stub_predicate_true
)

stub_pattern_4 = BoboPattern() \
    .followed_by(
    label=LABEL_A,
    predicate=stub_predicate_true
).followed_by(
    label=LABEL_B,
    predicate=stub_predicate_true
).followed_by(
    label=LABEL_C,
    predicate=stub_predicate_true
).followed_by(
    label=LABEL_D,
    predicate=stub_predicate_true
)


class TestBoboSetup(unittest.TestCase):

    def test_setup_minimum_configuration(self):
        setup = BoboSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_DEF_A,
                pattern=stub_pattern_1
            ))
        setup.configure()

        self.assertTrue(setup.is_configured())

        self.assertTrue(setup.get_receiver().is_active())
        self.assertTrue(setup.get_decider().is_active())
        self.assertTrue(setup.get_producer().is_active())
        self.assertTrue(setup.get_forwarder().is_active())

    def test_primitive_from_receiver_to_decider(self):
        setup = BoboSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_DEF_A,
                pattern=stub_pattern_4
            ))
        setup.config_receiver(StrDictValidator())
        setup.configure()

        receiver = setup.get_receiver()
        receiver.setup()

        decider = setup.get_decider()
        decider.setup()

        receiver.add_data(DATA_DICT_A)
        receiver.loop()
        decider.loop()

        handlers = decider.get_all_handlers()
        self.assertEqual(1, len(handlers))
        self.assertEqual(NAME_DEF_A, handlers[0].nfa.name)
