import unittest

from bobocep.receiver.bobo_null_data_generator import \
    BoboNullDataGenerator
from bobocep.receiver.bobo_receiver import BoboReceiver
from bobocep.receiver.formatters.primitive_event_formatter import \
    PrimitiveEventFormatter
from bobocep.receiver.validators.str_dict_validator import StrDictValidator


class TestBoboNullEventGenerator(unittest.TestCase):

    def test_process_then_cancel(self):
        receiver = BoboReceiver(StrDictValidator(), PrimitiveEventFormatter())
        null_data = {"key": "value"}

        nullgen = BoboNullDataGenerator(receiver=receiver,
                                        null_data=null_data)

        self.assertEqual(null_data, nullgen.null_data)
        self.assertFalse(nullgen._cancelled)

        nullgen.setup()

        # attempt without activating generator
        nullgen.loop()
        self.assertEqual(0, receiver._data_queue.qsize())

        # activate
        nullgen.activate()
        nullgen.loop()
        self.assertEqual(1, receiver._data_queue.qsize())
        self.assertEqual(null_data, receiver._data_queue.get_nowait())

        # cancel
        nullgen.cancel()
        self.assertTrue(nullgen._cancelled)
