import unittest

from bobocep.receiver.validators.any_validator import AnyValidator


class TestAnyValidator(unittest.TestCase):

    def test_true(self):
        self.assertTrue(AnyValidator().validate({}))
