import unittest

from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.events.primitive_event import PrimitiveEvent


class TestBoboHistory(unittest.TestCase):

    def test_to_dict(self):
        # Create primitive event
        p_timestamp = EpochNSClock.generate_timestamp()
        p_data = "p_data"
        p_event = PrimitiveEvent(
            timestamp=p_timestamp,
            data=p_data
        )
        p_hist = "p_hist"

        # Create composite event
        c_timestamp = EpochNSClock.generate_timestamp()
        c_name = "c_name"
        c_history = BoboHistory()
        c_data = "c_data"
        c_event = CompositeEvent(
            timestamp=c_timestamp,
            name=c_name,
            history=c_history,
            data=c_data
        )
        c_hist = "c_hist"

        # Create list of events for history
        events = {
            p_hist: [p_event],
            c_hist: [c_event]
        }

        # Create history and add events
        history = BoboHistory(events=events)

        self.assertDictEqual(history.to_dict(), {
            p_hist: [p_event.to_dict()],
            c_hist: [c_event.to_dict()]
        })
