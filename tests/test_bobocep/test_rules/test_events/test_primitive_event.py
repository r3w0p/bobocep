import unittest

from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.events.primitive_event import PrimitiveEvent


class TestPrimitiveEvent(unittest.TestCase):

    def test_to_dict(self):
        p_timestamp = EpochNSClock.generate_timestamp()
        p_data = {"p_key": "p_value"}

        p_event = PrimitiveEvent(
            timestamp=p_timestamp,
            data=p_data
        )

        self.assertDictEqual(p_event.to_dict(), {
            PrimitiveEvent.TIMESTAMP: p_timestamp,
            PrimitiveEvent.DATA: p_data,
            PrimitiveEvent.EVENT_ID: p_event.event_id
        })
