import unittest

from bobocep.decider.buffers.match_event import MatchEvent
from bobocep.decider.runs.bobo_run import BoboRun
from bobocep.decider.versions.run_version import RunVersion
from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.rules.nfas.patterns.bobo_pattern import BoboPattern
from bobocep.rules.predicates.bobo_predicate_function import \
    BoboPredicateFunction

NFA_NAME_A = "NFA_NAME_A"

LABEL_LAYER_A = 'layer_a'
LABEL_LAYER_B = 'layer_b'
LABEL_LAYER_C = 'layer_c'

stub_predicate = BoboPredicateFunction(lambda e, h: True)

stub_pattern = BoboPattern() \
    .followed_by(LABEL_LAYER_A, stub_predicate) \
    .followed_by(LABEL_LAYER_B, stub_predicate) \
    .followed_by(LABEL_LAYER_C, stub_predicate)


class TestMatchEvent(unittest.TestCase):

    def test_match_event_points_to_itself(self):
        event_a = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())

        match_a = MatchEvent(nfa_name=NFA_NAME_A,
                             label=LABEL_LAYER_A,
                             event=event_a)

        version = RunVersion()
        version.add_level(BoboRun._generate_id(
            nfa_name=NFA_NAME_A,
            start_event_id=event_a.id))
        version_str = version.get_version_as_str()

        with self.assertRaises(RuntimeError):
            match_a.add_pointer_next(
                version=version_str,
                label=LABEL_LAYER_A,
                event_id=event_a.id)

        with self.assertRaises(RuntimeError):
            match_a.add_pointer_previous(
                version=version_str,
                label=LABEL_LAYER_A,
                event_id=event_a.id)

    def test_remove_all_pointers_two_match_events(self):
        event_a = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())
        event_b = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())

        match_a = MatchEvent(nfa_name=NFA_NAME_A,
                             label=LABEL_LAYER_A,
                             event=event_a)
        match_b = MatchEvent(nfa_name=NFA_NAME_A,
                             label=LABEL_LAYER_B,
                             event=event_b)

        version = RunVersion()
        version.add_level(BoboRun._generate_id(
            nfa_name=NFA_NAME_A,
            start_event_id=event_a.id))
        version_str = version.get_version_as_str()

        # match events should start with no pointers
        self.assertFalse(match_a.has_pointers())
        self.assertFalse(match_b.has_pointers())

        # match a --next--> match b
        match_a.add_pointer_next(version=version_str,
                                 event_id=match_b.event.id)

        # match a <--previous-- match b
        match_b.add_pointer_previous(version=version_str,
                                     event_id=match_a.event.id)

        # match events both have pointers
        self.assertTrue(match_a.has_pointers())
        self.assertTrue(match_b.has_pointers())

        # removing pointers from one match event
        match_a.remove_all_pointers(version=version_str)

        self.assertFalse(match_a.has_pointers())
        self.assertTrue(match_b.has_pointers())

        # all pointers removed
        match_b.remove_all_pointers(version=version_str)

        self.assertFalse(match_a.has_pointers())
        self.assertFalse(match_b.has_pointers())

    def test_to_dict_two_match_events(self):
        event_a = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())
        event_b = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())

        match_a = MatchEvent(nfa_name=NFA_NAME_A,
                             label=LABEL_LAYER_A,
                             event=event_a)
        match_b = MatchEvent(nfa_name=NFA_NAME_A,
                             label=LABEL_LAYER_B,
                             event=event_b)

        version = RunVersion()
        version.add_level(BoboRun._generate_id(
            nfa_name=NFA_NAME_A,
            start_event_id=event_a.id))
        version_str = version.get_version_as_str()

        # match a --next--> match b
        match_a.add_pointer_next(version=version_str,
                                 label=match_b.label,
                                 event_id=match_b.event.id)

        # match a dict
        self.assertDictEqual(match_a.to_dict(), {
            MatchEvent.NFA_NAME: NFA_NAME_A,
            MatchEvent.LABEL: LABEL_LAYER_A,
            MatchEvent.EVENT: event_a.to_dict(),
            MatchEvent.NEXT_IDS: {
                version_str: (match_b.label, match_b.event.id)
            },
            MatchEvent.PREVIOUS_IDS: {}
        })

        # match a <--previous-- match b
        match_b.add_pointer_previous(version=version_str,
                                     label=match_a.label,
                                     event_id=match_a.event.id)

        # match b dict
        self.assertDictEqual(match_b.to_dict(), {
            MatchEvent.NFA_NAME: NFA_NAME_A,
            MatchEvent.LABEL: LABEL_LAYER_B,
            MatchEvent.EVENT: event_b.to_dict(),
            MatchEvent.NEXT_IDS: {},
            MatchEvent.PREVIOUS_IDS: {
                version_str: (match_a.label, match_a.event.id)
            }
        })
