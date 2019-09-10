import unittest

from bobocep.forwarder.action_forwarder import ActionForwarder
from bobocep.forwarder.forwarder_subscriber import IForwarderSubscriber
from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.actions.no_action import NoAction
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory

NAME_A = "name_a"


def generate_composite_event(name: str) -> CompositeEvent:
    return CompositeEvent(
        timestamp=EpochNSClock.generate_timestamp(),
        name=name,
        history=BoboHistory(),
        data={})


class StubForwarderSubscriber(IForwarderSubscriber):

    def __init__(self) -> None:
        super().__init__()

        self.success = []
        self.failure = []

    def on_forwarder_success_event(self, event: CompositeEvent) -> None:
        self.success.append(event)

    def on_forwarder_failure_event(self, event: CompositeEvent) -> None:
        self.failure.append(event)


class TestActionForwarder(unittest.TestCase):

    def test_subscribe_unsubscribe(self):
        forward = ActionForwarder(NoAction())
        sub = StubForwarderSubscriber()

        forward.subscribe(sub)
        self.assertListEqual([sub], forward._subs)

        forward.unsubscribe(sub)
        self.assertListEqual([], forward._subs)

    def test_forward_successful(self):
        comp_event = generate_composite_event(NAME_A)
        action_event = NoAction().execute(comp_event)

        # True = Success
        forward = ActionForwarder(NoAction(bool_return=True))

        sub = StubForwarderSubscriber()
        forward.subscribe(sub)

        forward.on_action_attempt(action_event)
        forward.setup()
        forward.loop()

        self.assertListEqual([action_event], sub.success)

    def test_forward_failure(self):
        comp_event = generate_composite_event(NAME_A)
        action_event = NoAction().execute(comp_event)

        # False = Failure
        forward = ActionForwarder(NoAction(bool_return=False))

        sub = StubForwarderSubscriber()
        forward.subscribe(sub)

        forward.on_action_attempt(action_event)
        forward.setup()
        forward.loop()

        self.assertListEqual([action_event], sub.failure)
