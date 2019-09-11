import unittest

from bobocep.receiver.bobo_receiver import BoboReceiver
from bobocep.receiver.formatters.primitive_event_formatter import \
    PrimitiveEventFormatter
from bobocep.receiver.generators.bobo_null_data_generator import \
    BoboNullDataGenerator
from bobocep.receiver.generators.data.bobo_null_data import BoboNullData
from bobocep.receiver.validators.str_dict_validator import StrDictValidator

KEY_A = "key_a"
VALUE_A = "value_a"
DATA_A = {KEY_A: VALUE_A}


class StubBoboNullDictData(BoboNullData):

    def __init__(self, data: dict) -> None:
        super().__init__()

        self.data = data

    def get_null_data(self) -> dict:
        return self.data


class TestBoboNullEventGenerator(unittest.TestCase):

    def test_cancel(self):
        receiver = BoboReceiver(validator=StrDictValidator(),
                                formatter=PrimitiveEventFormatter())
        null_data = StubBoboNullDictData(data=DATA_A)

        nullgen = BoboNullDataGenerator(
            receiver=receiver,
            null_data=null_data,
            active=True)

        nullgen.setup()
        nullgen.loop()
        self.assertEqual(1, receiver._data_queue.qsize())

        nullgen.cancel()
        self.assertTrue(nullgen._cancelled)

        with self.assertRaises(RuntimeError):
            nullgen.loop()

    def test_activate_deactivate(self):
        receiver = BoboReceiver(
            validator=StrDictValidator(),
            formatter=PrimitiveEventFormatter())
        null_data = StubBoboNullDictData(data=DATA_A)

        nullgen = BoboNullDataGenerator(
            receiver=receiver,
            null_data=null_data,
            active=False)

        nullgen.setup()
        nullgen.loop()
        self.assertEqual(0, receiver._data_queue.qsize())

        nullgen.activate()
        nullgen.loop()
        self.assertEqual(1, receiver._data_queue.qsize())

        nullgen.deactivate()
        nullgen.loop()
        self.assertEqual(1, receiver._data_queue.qsize())
