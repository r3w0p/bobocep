import unittest

from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.actions.no_action import NoAction
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory


class TestNoAction(unittest.TestCase):

    def test_true(self):
        timestamp = EpochNSClock.generate_timestamp()
        name = "c_name"
        history = BoboHistory()
        data = {"c_key": "c_value"}

        c_event = CompositeEvent(timestamp=timestamp,
                                 name=name,
                                 history=history,
                                 data=data)

        self.assertTrue(NoAction().perform_action(c_event))
