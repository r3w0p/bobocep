import unittest

from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.receiver.validators.str_dict_validator import StrDictValidator
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.events.primitive_event import PrimitiveEvent

KEY_A = "key_a"
VAL_A = "value_a"


class TestStrDictValidator(unittest.TestCase):

    def test_valid_min_0(self):
        validator = StrDictValidator(min_length=0)

        self.assertTrue(validator.validate({}))
        self.assertTrue(validator.validate({KEY_A: VAL_A}))

    def test_invalid_min_0(self):
        validator = StrDictValidator(min_length=0)

        self.assertFalse(validator.validate(None))
        self.assertFalse(validator.validate(""))
        self.assertFalse(validator.validate(123))
        self.assertFalse(validator.validate(123.456))
        self.assertFalse(validator.validate(True))
        self.assertFalse(validator.validate(False))
        self.assertFalse(validator.validate(BoboHistory()))
        self.assertFalse(validator.validate(
            PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())))

        # as a dict
        self.assertFalse(validator.validate({KEY_A: None}))
        self.assertFalse(validator.validate({KEY_A: 123}))
        self.assertFalse(validator.validate({KEY_A: 123.456}))
        self.assertFalse(validator.validate({KEY_A: True}))
        self.assertFalse(validator.validate({KEY_A: False}))
        self.assertFalse(validator.validate({KEY_A: BoboHistory()}))
        self.assertFalse(validator.validate({
            KEY_A: PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())
        }))

    def test_invalid_min_1(self):
        validator = StrDictValidator(min_length=1)

        self.assertFalse(validator.validate({KEY_A: ""}))
        self.assertFalse(validator.validate({"": VAL_A}))
