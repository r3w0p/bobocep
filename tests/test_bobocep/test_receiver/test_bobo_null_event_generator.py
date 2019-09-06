import unittest

from bobocep.receiver.bobo_receiver import BoboReceiver
from bobocep.receiver.formatters.primitive_event_formatter import \
    PrimitiveEventFormatter
from bobocep.receiver.generators.bobo_null_data_generator import \
    BoboNullDataGenerator
from bobocep.receiver.generators.bobo_null_data_rand_int import \
    BoboNullDataRandInt
from bobocep.receiver.validators.str_dict_validator import StrDictValidator


class TestBoboNullEventGenerator(unittest.TestCase):

    def test_process_then_cancel(self):
        imin = 1
        imax = 10
        receiver = BoboReceiver(StrDictValidator(), PrimitiveEventFormatter())
        null_data = BoboNullDataRandInt(imin=imin, imax=imax)

        nullgen = BoboNullDataGenerator(
            receiver=receiver,
            null_data=null_data)
        nullgen.setup()

        # attempt without activating generator
        nullgen.loop()
        self.assertEqual(0, receiver._data_queue.qsize())

        # activate
        nullgen.activate()
        nullgen.loop()
        self.assertEqual(1, receiver._data_queue.qsize())
        self.assertTrue(imin <= receiver._data_queue.get_nowait() <= imax)

        # cancel
        nullgen.cancel()
        self.assertTrue(nullgen._cancelled)
