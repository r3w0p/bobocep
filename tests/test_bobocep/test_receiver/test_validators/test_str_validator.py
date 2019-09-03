import unittest

from bobocep.receiver.validators.str_validator import StrValidator
from bobocep.rules.events.histories.bobo_history import BoboHistory


class TestStrValidator(unittest.TestCase):

    def test_no_minimum_length(self):
        val = StrValidator(min_length=0)

        self.assertTrue(val.validate(""))
        self.assertTrue(val.validate("abc"))

    def test_minimum_length(self):
        val = StrValidator(min_length=5)

        self.assertFalse(val.validate(""))
        self.assertFalse(val.validate("abc"))
        self.assertTrue(val.validate("hello"))
        self.assertTrue(val.validate("goodbye"))

    def test_invalid(self):
        val = StrValidator(min_length=0)

        self.assertFalse(val.validate(None))
        self.assertFalse(val.validate(123))
        self.assertFalse(val.validate(BoboHistory()))
