import unittest
from typing import List

from bobocep.decider.buffers.shared_versioned_match_buffer import \
    SharedVersionedMatchBuffer
from bobocep.decider.dist_decider import DistDecider
from bobocep.decider.handlers.bobo_nfa_handler import BoboNFAHandler
from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.bobo_rule_builder import BoboRuleBuilder
from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.rules.nfas.patterns.bobo_pattern import BoboPattern
from bobocep.rules.predicates.bobo_predicate_callable import \
    BoboPredicateCallable


def stub_predicate(event: BoboEvent,
                   history: BoboHistory,
                   recents: List[CompositeEvent]):
    return True


stub_pattern = BoboPattern() \
    .followed_by('layer_1', BoboPredicateCallable(stub_predicate)) \
    .followed_by('layer_2', BoboPredicateCallable(stub_predicate)) \
    .followed_by('layer_3', BoboPredicateCallable(stub_predicate))

stub_nfa = BoboRuleBuilder.nfa('nfa_name', stub_pattern)


class TestDistDecider(unittest.TestCase):

    def test_on_sync(self):
        decider = DistDecider()
        self.assertFalse(decider.is_synced)

        decider.on_sync()
        self.assertTrue(decider.is_synced)

    def test_sync_process_new_events(self):
        handler = BoboNFAHandler(nfa=stub_nfa,
                                 buffer=SharedVersionedMatchBuffer())

        p_event = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())

        c_event = CompositeEvent(timestamp=EpochNSClock.generate_timestamp(),
                                 name='c_name',
                                 history=BoboHistory())

        decider = DistDecider()
        decider.add_nfa_handler(handler)

        # Not synced, so will not accept events
        decider.on_receiver_event(p_event)
        self.assertEqual(0, decider._event_queue.qsize())

        decider.on_accepted_producer_event(c_event)
        self.assertEqual(0, decider._event_queue.qsize())

        # Sync distributed decider
        decider.on_sync()

        # Add event and process, causes handler to generate a run
        decider.on_receiver_event(p_event)
        decider.setup()
        decider.loop()
        self.assertEqual(1, len(handler._runs.values()))

        decider.on_accepted_producer_event(c_event)
        decider.loop()
        self.assertEqual(2, len(handler._runs.values()))
