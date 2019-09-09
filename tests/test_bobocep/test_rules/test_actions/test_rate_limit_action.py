import unittest
from time import sleep

from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.actions.rate_limit_action import RateLimitAction
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory

NAME_A = "name_a"
NAME_B = "name_b"
NAME_C = "name_c"

RATE_A = 10
RATE_B = 20
RATE_C = 30

LIMIT_A = {NAME_A: RATE_A}

LIMIT_AB = {
    NAME_A: RATE_A,
    NAME_B: RATE_B
}

LIMIT_ABC = {
    NAME_A: RATE_A,
    NAME_B: RATE_B,
    NAME_C: RATE_C
}


def generate_composite_event(name: str) -> CompositeEvent:
    return CompositeEvent(
        timestamp=EpochNSClock.generate_timestamp(),
        name=name,
        history=BoboHistory(),
        data={})


class TestRateLimitAction(unittest.TestCase):

    def test_get_limits(self):
        action = RateLimitAction(limit_dict=LIMIT_AB)
        self.assertDictEqual(LIMIT_AB, action.get_limits())

        action.set_limit(NAME_C, RATE_C)
        self.assertDictEqual(LIMIT_ABC, action.get_limits())

    def test_two_events_same_name_no_rate(self):
        event_a = generate_composite_event(NAME_A)
        event_b = generate_composite_event(NAME_A)

        action = RateLimitAction()

        self.assertTrue(action.execute(event_a)[0])
        self.assertTrue(action.execute(event_b)[0])

    def test_two_events_same_name_before_rate_elapse(self):
        event_a1 = generate_composite_event(NAME_A)
        event_a2 = generate_composite_event(NAME_A)

        action = RateLimitAction(limit_dict=LIMIT_A)

        self.assertTrue(action.execute(event_a1)[0])
        self.assertFalse(action.execute(event_a2)[0])

    def test_two_events_same_name_after_rate_elapse(self):
        rate = 1
        event_a1 = generate_composite_event(NAME_A)
        sleep(rate + 1)
        event_a2 = generate_composite_event(NAME_A)

        action = RateLimitAction(limit_dict={NAME_A: rate})

        self.assertTrue(action.execute(event_a1)[0])
        self.assertTrue(action.execute(event_a2)[0])

    def test_three_events_different_names_two_limited(self):
        event_a = generate_composite_event(NAME_A)
        event_b = generate_composite_event(NAME_B)
        event_c = generate_composite_event(NAME_C)

        action = RateLimitAction(limit_dict=LIMIT_AB)

        self.assertTrue(action.execute(event_a)[0])
        self.assertTrue(action.execute(event_b)[0])
        self.assertTrue(action.execute(event_c)[0])
