import unittest

from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory


class TestCompositeEvent(unittest.TestCase):

    def test_to_dict(self):
        c_timestamp = EpochNSClock.generate_timestamp()
        c_name = "c_name"
        c_history = BoboHistory()
        c_data = {"c_key": "c_value"}

        c_event = CompositeEvent(
            timestamp=c_timestamp,
            name=c_name,
            history=c_history,
            data=c_data
        )

        self.assertDictEqual(c_event.to_dict(), {
            CompositeEvent.TIMESTAMP: c_timestamp,
            CompositeEvent.NAME: c_name,
            CompositeEvent.HISTORY: c_history.to_dict(),
            CompositeEvent.DATA: c_data,
            CompositeEvent.EVENT_ID: c_event.event_id
        })
