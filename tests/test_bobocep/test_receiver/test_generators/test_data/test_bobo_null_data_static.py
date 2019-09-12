import unittest

from bobocep.receiver.generators.data.bobo_null_data_static import \
    BoboNullDataStatic


class TestBoboNullDataStatic(unittest.TestCase):

    def test_get_static_data(self):
        data = "123"
        self.assertEqual(data, BoboNullDataStatic(data).get_null_data())
