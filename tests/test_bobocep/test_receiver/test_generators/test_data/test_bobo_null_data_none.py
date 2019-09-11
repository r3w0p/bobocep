import unittest

from bobocep.receiver.generators.data.bobo_null_data_none import \
    BoboNullDataNone


class TestBoboNullDataNone(unittest.TestCase):

    def test_get_null_data(self):
        self.assertIsNone(BoboNullDataNone().get_null_data())
