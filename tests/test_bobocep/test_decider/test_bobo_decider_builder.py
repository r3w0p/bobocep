import unittest

from bobocep.decider.bobo_decider_builder import BoboDeciderBuilder
from bobocep.decider.buffers.match_event import MatchEvent
from bobocep.decider.buffers.shared_versioned_match_buffer import \
    SharedVersionedMatchBuffer
from bobocep.decider.runs.bobo_run import BoboRun
from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.bobo_rule_builder import BoboRuleBuilder
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.rules.nfas.patterns.bobo_pattern import BoboPattern
from bobocep.rules.predicates.bobo_predicate_function import \
    BoboPredicateFunction

NFA_NAME_A = "NFA_NAME_A"
RUN_ID_A = "run_id_a"
VERSION_A = "version_a"

LABEL_LAYER_A = 'layer_a'
LABEL_LAYER_B = 'layer_b'
LABEL_LAYER_C = 'layer_c'

KEY_NEXT_A = "key_next_a"
VAL_NEXT_A = ("label_next_a", "id_next_a")

KEY_PREV_A = "key_prev_a"
VAL_PREV_A = ("label_prev_a", "id_prev_a")

NEXT_IDS_A = {KEY_NEXT_A: VAL_NEXT_A}
PREV_IDS_A = {KEY_PREV_A: VAL_PREV_A}

event_a = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())

stub_predicate = BoboPredicateFunction(lambda e, h: True)

stub_pattern = BoboPattern() \
    .followed_by(LABEL_LAYER_A, stub_predicate) \
    .followed_by(LABEL_LAYER_B, stub_predicate) \
    .followed_by(LABEL_LAYER_C, stub_predicate)


class TestBoboDeciderBuilder(unittest.TestCase):

    def test_match_event(self):
        original = MatchEvent(
            nfa_name=NFA_NAME_A,
            label=LABEL_LAYER_A,
            event=event_a,
            next_ids=NEXT_IDS_A,
            previous_ids=PREV_IDS_A
        )

        generated = BoboDeciderBuilder \
            .match_event(original.to_dict())

        self.assertEqual(original.nfa_name,
                         generated.nfa_name)
        self.assertEqual(original.label,
                         generated.label)
        self.assertDictEqual(original.event.to_dict(),
                             generated.event.to_dict())
        self.assertDictEqual(original.next_ids,
                             generated.next_ids)
        self.assertDictEqual(original.previous_ids,
                             generated.previous_ids)

    def test_shared_versioned_match_buffer(self):
        original = SharedVersionedMatchBuffer()
        original.put_event(nfa_name=NFA_NAME_A,
                           run_id=RUN_ID_A,
                           version=VERSION_A,
                           state_label=LABEL_LAYER_A,
                           event=event_a)

        # ensure event is found in original buffer
        event_orig = original.get_event(nfa_name=NFA_NAME_A,
                                        state_label=LABEL_LAYER_A,
                                        event_id=event_a.id,
                                        default=None)
        self.assertIsNotNone(event_orig)
        self.assertEqual(event_orig, event_a)

        # generate new buffer
        generated = BoboDeciderBuilder \
            .shared_versioned_match_buffer(original.to_dict())

        # ensure event is found in generated buffer
        event_gen = generated.get_event(nfa_name=NFA_NAME_A,
                                        state_label=LABEL_LAYER_A,
                                        event_id=event_a.id,
                                        default=None)
        self.assertIsNotNone(event_gen)

        # ensure events match between buffers
        self.assertDictEqual(event_orig.to_dict(),
                             event_gen.to_dict())

    def test_bobo_run(self):
        buffer_orig = SharedVersionedMatchBuffer()
        nfa_orig = BoboRuleBuilder.nfa(
            name_nfa=NFA_NAME_A,
            pattern=stub_pattern)

        original = BoboRun(buffer=buffer_orig,
                           nfa=nfa_orig,
                           event=event_a)

        generated = BoboDeciderBuilder \
            .run(d=original.to_dict(),
                 buffer=original.buffer,
                 nfa=original.nfa)

        self.assertEqual(original.buffer,
                         generated.buffer)
        self.assertEqual(original.nfa,
                         generated.nfa)
        self.assertDictEqual(original.event.to_dict(),
                             generated.event.to_dict())
        self.assertEqual(original.start_time,
                         generated.start_time)
        self.assertEqual(original.start_state,
                         generated.start_state)
        self.assertEqual(original.current_state,
                         generated.current_state)
        self.assertEqual(original.id,
                         generated.id)
        self.assertEqual(original.version.get_version_as_str(),
                         generated.version.get_version_as_str())
        self.assertEqual(original.last_process_cloned(),
                         generated.last_process_cloned())
        self.assertEqual(original.is_halted(),
                         generated.is_halted())
