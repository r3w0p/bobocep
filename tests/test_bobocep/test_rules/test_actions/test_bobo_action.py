import unittest

from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.actions.bobo_action import BoboAction
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory


class StubBoboAction(BoboAction):

    def __init__(self) -> None:
        super().__init__()

        self.events = []

    def _perform_action(self, event: CompositeEvent) -> bool:
        self.events.append(event)
        return True


class TestBoboAction(unittest.TestCase):

    def test_true(self):
        timestamp = EpochNSClock.generate_timestamp()
        name = "c_name"
        history = BoboHistory()
        data = {"c_key": "c_value"}

        c_event = CompositeEvent(timestamp=timestamp,
                                 name=name,
                                 history=history,
                                 data=data)

        stubaction = StubBoboAction()

        self.assertTrue(stubaction.execute(c_event)[0])
        self.assertListEqual([c_event], stubaction.events)
