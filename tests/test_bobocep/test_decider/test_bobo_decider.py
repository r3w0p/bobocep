import unittest

from bobocep.decider.bobo_decider import BoboDecider
from bobocep.decider.buffers.shared_versioned_match_buffer import \
    SharedVersionedMatchBuffer
from bobocep.decider.decider_subscriber import IDeciderSubscriber
from bobocep.decider.handlers.bobo_nfa_handler import BoboNFAHandler
from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.bobo_rule_builder import BoboRuleBuilder
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.rules.nfas.patterns.bobo_pattern import BoboPattern
from bobocep.rules.predicates.bobo_predicate_function import \
    BoboPredicateFunction

NFA_NAME_A = "NFA_NAME_A"

LABEL_LAYER_A = 'layer_a'
LABEL_LAYER_B = 'layer_b'
LABEL_LAYER_C = 'layer_c'
LABEL_LAYER_D = 'layer_d'

COMPOSITE_NAME = "c_name"

event_a = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())
event_b = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())
event_c = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())

event_comp = CompositeEvent(
    timestamp=EpochNSClock.generate_timestamp(),
    name=COMPOSITE_NAME,
    history=BoboHistory())

stub_predicate = BoboPredicateFunction(lambda e, h: True)

stub_pattern = BoboPattern() \
    .followed_by(LABEL_LAYER_A, stub_predicate) \
    .followed_by(LABEL_LAYER_B, stub_predicate) \
    .followed_by(LABEL_LAYER_C, stub_predicate) \
    .followed_by(LABEL_LAYER_D, stub_predicate)

stub_nfa = BoboRuleBuilder.nfa(NFA_NAME_A, stub_pattern)


class NFAHandlerSubscriber(IDeciderSubscriber):

    def __init__(self) -> None:
        super().__init__()

        self.final = []
        self.final_history = []

    def on_decider_complex_event(self, nfa_name: str,
                                 history: BoboHistory) -> None:
        self.final.append(nfa_name)
        self.final_history.append(history)


class TestBoboDecider(unittest.TestCase):

    def test_add_nfa_handler(self):
        handler1 = BoboNFAHandler(
            nfa=stub_nfa,
            buffer=SharedVersionedMatchBuffer())

        handler2 = BoboNFAHandler(
            nfa=stub_nfa,
            buffer=SharedVersionedMatchBuffer())

        decider = BoboDecider()
        decider.add_nfa_handler(handler1)

        self.assertDictEqual(decider._nfa_handlers, {
            handler1.nfa.name: handler1
        })

        # two handlers with same nfa name
        with self.assertRaises(RuntimeError):
            decider.add_nfa_handler(handler2)

    def test_new_event(self):
        decider = BoboDecider()

        decider.on_receiver_event(event_a)
        self.assertEqual(event_a, decider._event_queue.get_nowait())

        decider.on_receiver_event(event_comp)
        self.assertEqual(event_comp, decider._event_queue.get_nowait())

    def test_on_accepted_producer_event(self):
        decider = BoboDecider()

        decider.on_accepted_producer_event(event_comp)
        self.assertEqual(event_comp, decider._event_queue.get_nowait())

    def test_process(self):
        handler = BoboNFAHandler(
            nfa=stub_nfa,
            buffer=SharedVersionedMatchBuffer())

        p_event = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())

        # Add handler and event
        decider = BoboDecider()
        decider.add_nfa_handler(handler)
        decider.on_receiver_event(p_event)

        # Process even in decider's queue
        decider.setup()
        decider.loop()

        # A new run should have been created in the handler
        self.assertEqual(1, len(handler._runs.values()))

    def test_subscribe_unsubscribe(self):
        decider = BoboDecider()
        subscriber = NFAHandlerSubscriber()

        # no handler for nfa in decider yet
        with self.assertRaises(RuntimeError):
            decider.subscribe(stub_nfa.name, subscriber)

        handler = BoboNFAHandler(
            nfa=stub_nfa,
            buffer=SharedVersionedMatchBuffer())
        decider.add_nfa_handler(handler)

        # subscribe
        decider.subscribe(stub_nfa.name, subscriber)
        self.assertDictEqual(decider._subs, {
            stub_nfa.name: [subscriber]
        })

        # unsubscribe
        decider.unsubscribe(stub_nfa.name, subscriber)
        self.assertDictEqual(decider._subs, {
            stub_nfa.name: []
        })

    def test_to_dict(self):
        decider = BoboDecider()

        # before handler
        self.assertDictEqual({
            BoboDecider.HANDLERS: []
        }, decider.to_dict())

        # add handler
        handler = BoboNFAHandler(
            nfa=stub_nfa,
            buffer=SharedVersionedMatchBuffer())
        decider.add_nfa_handler(handler)

        # after handler
        self.assertDictEqual({
            BoboDecider.HANDLERS: [handler.to_dict()]
        }, decider.to_dict())
