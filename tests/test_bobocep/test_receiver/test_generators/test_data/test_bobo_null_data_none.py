import unittest

from bobocep.receiver.bobo_receiver import BoboReceiver
from bobocep.receiver.formatters.primitive_event_formatter import \
    PrimitiveEventFormatter
from bobocep.receiver.generators.data.bobo_null_data_none import BoboNullDataNone
from bobocep.receiver.generators.data.bobo_null_data import BoboNullData
from bobocep.receiver.validators.str_dict_validator import StrDictValidator


class TestBoboNullDataNone(unittest.TestCase):

    def test_get_null_data(self):
        self.assertIsNone(BoboNullDataNone().get_null_data())
