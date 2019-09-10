import unittest

from bobocep.producer.action_producer import ActionProducer
from bobocep.producer.producer_subscriber import IProducerSubscriber
from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.actions.no_action import NoAction
from bobocep.rules.events.action_event import ActionEvent
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory

NAME_A = "name_a"


def generate_composite_event(name: str) -> CompositeEvent:
    return CompositeEvent(
        timestamp=EpochNSClock.generate_timestamp(),
        name=name,
        history=BoboHistory(),
        data={})


class StubProducerSubscriber(IProducerSubscriber):

    def __init__(self) -> None:
        super().__init__()

        self.accept = []
        self.reject = []
        self.action = []

    def on_accepted_producer_event(self, event: CompositeEvent) -> None:
        self.accept.append(event)

    def on_rejected_producer_event(self, event: CompositeEvent) -> None:
        self.reject.append(event)

    def on_producer_action(self, event: ActionEvent):
        self.action.append(event)


class TestActionProducer(unittest.TestCase):

    def test_subscribe_unsubscribe(self):
        prod = ActionProducer(NoAction())
        sub = StubProducerSubscriber()

        # subscribe
        prod.subscribe(NAME_A, sub)
        self.assertDictEqual(prod._subs, {
            NAME_A: [sub]
        })

        # unsubscribe
        prod.unsubscribe(NAME_A, sub)
        self.assertDictEqual(prod._subs, {
            NAME_A: []
        })

    def test_action_true(self):
        event_a = generate_composite_event(NAME_A)
        prod = ActionProducer(NoAction(bool_return=True))

        sub = StubProducerSubscriber()
        prod.subscribe(NAME_A, sub)

        prod.on_decider_complex_event(event_a)
        prod.setup()
        prod.loop()

        self.assertListEqual([event_a], sub.accept)

    def test_action_false(self):
        event_a = generate_composite_event(NAME_A)
        prod = ActionProducer(NoAction(bool_return=False))

        sub = StubProducerSubscriber()
        prod.subscribe(NAME_A, sub)

        prod.on_decider_complex_event(event_a)
        prod.setup()
        prod.loop()

        self.assertListEqual([event_a], sub.reject)
