import unittest
from uuid import uuid4

from bobocep.decider.buffers.match_event import MatchEvent
from bobocep.decider.buffers.shared_versioned_match_buffer import \
    SharedVersionedMatchBuffer
from bobocep.decider.versions.run_version import RunVersion
from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.rules.nfas.patterns.bobo_pattern import BoboPattern
from bobocep.rules.predicates.bobo_predicate_function import \
    BoboPredicateFunction

NFA_NAME_A = "NFA_NAME_A"
NFA_NAME_B = "NFA_NAME_B"

LABEL_LAYER_A = 'layer_a'
LABEL_LAYER_B = 'layer_b'
LABEL_LAYER_C = 'layer_c'

event_a = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())
event_b = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())
event_c = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())

stub_predicate = BoboPredicateFunction(lambda e, h, r: True)

stub_pattern = BoboPattern() \
    .followed_by(LABEL_LAYER_A, stub_predicate) \
    .followed_by(LABEL_LAYER_B, stub_predicate) \
    .followed_by(LABEL_LAYER_C, stub_predicate)


def generate_unique_string():
    return "{}-{}".format(uuid4(), EpochNSClock.generate_timestamp())


class TestSharedVersionedMatchBuffer(unittest.TestCase):

    def test_put_and_get_event(self):
        buffer = SharedVersionedMatchBuffer()
        run_id = generate_unique_string()
        version = RunVersion()
        version.add_level(run_id)

        buffer.put_event(nfa_name=NFA_NAME_A,
                         run_id=run_id,
                         version=version.get_version_as_str(),
                         state_label=LABEL_LAYER_A,
                         event=event_a)

        self.assertEqual(event_a,
                         buffer.get_event(
                             nfa_name=NFA_NAME_A,
                             state_label=LABEL_LAYER_A,
                             event_id=event_a.id,
                             default=None))

        # incorrect nfa name
        self.assertIsNone(
            buffer.get_event(nfa_name=NFA_NAME_B,
                             state_label=LABEL_LAYER_A,
                             event_id=event_a.id,
                             default=None))

        # incorrect state label
        self.assertIsNone(
            buffer.get_event(nfa_name=NFA_NAME_A,
                             state_label=LABEL_LAYER_B,
                             event_id=event_a.id,
                             default=None))

        # incorrect event id
        self.assertIsNone(
            buffer.get_event(nfa_name=NFA_NAME_A,
                             state_label=LABEL_LAYER_A,
                             event_id=event_b.id,
                             default=None))

    def test_1_level_10_increments_1_event_per_increment(self):
        buffer = SharedVersionedMatchBuffer()
        run_id = generate_unique_string()

        events = [
            PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())
            for _ in range(10)]

        version = RunVersion()
        version.add_level(run_id)
        version_current = version.get_version_as_str()

        for event in events:
            version.increment_level(generate_unique_string())
            version_next = version.get_version_as_str()

            buffer.put_event(
                nfa_name=NFA_NAME_A,
                run_id=run_id,
                version=version_current,
                state_label=LABEL_LAYER_A,
                event=event,
                new_version=version_next)

            version_current = version_next

        history_events = buffer.get_all_events(
            nfa_name=NFA_NAME_A,
            run_id=run_id,
            version=version).events[LABEL_LAYER_A]

        self.assertEqual(10, len(history_events))

        for event in events:
            self.assertTrue(event in history_events)

    def test_1_level_10_increments_5_events_per_increment(self):
        buffer = SharedVersionedMatchBuffer()
        run_id = generate_unique_string()

        events_increments = [[
            PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())
            for _ in range(5)]  # events
            for _ in range(10)]  # increments

        version = RunVersion()
        version.add_level(run_id)
        version_current = version.get_version_as_str()

        for events in events_increments:
            version.increment_level(generate_unique_string())
            version_next = version.get_version_as_str()

            buffer.put_event(
                nfa_name=NFA_NAME_A,
                run_id=run_id,
                version=version_current,
                state_label=LABEL_LAYER_A,
                event=events[0],
                new_version=version_next)

            version_current = version_next

            for i in range(1, len(events)):
                buffer.put_event(
                    nfa_name=NFA_NAME_A,
                    run_id=run_id,
                    version=version_current,
                    state_label=LABEL_LAYER_A,
                    event=events[i])

        history_events = buffer.get_all_events(
            nfa_name=NFA_NAME_A,
            run_id=run_id,
            version=version).events[LABEL_LAYER_A]

        for events in events_increments:
            for event in events:
                self.assertTrue(event in history_events)

    def test_2_nfas_2_versions_1_increment(self):
        buffer = SharedVersionedMatchBuffer()

        run_id_a = generate_unique_string()
        run_id_a_incr = generate_unique_string()
        run_id_b = generate_unique_string()

        # create two versions for run a and run b
        version_a = RunVersion()
        version_a.add_level(run_id_a)
        version_a_str = version_a.get_version_as_str()

        version_b = RunVersion()
        version_b.add_level(run_id_b)

        # add event a into version a, run a
        buffer.put_event(nfa_name=NFA_NAME_A,
                         run_id=run_id_a,
                         version=version_a_str,
                         state_label=LABEL_LAYER_A,
                         event=event_a)

        # increment version a
        version_a.increment_level(generate_unique_string())
        version_a_incr_str = version_a.get_version_as_str()

        # add event b to version a incr, run a incr
        buffer.put_event(nfa_name=NFA_NAME_A,
                         run_id=run_id_a,
                         version=version_a_str,
                         state_label=LABEL_LAYER_B,
                         event=event_b,
                         new_run_id=run_id_a_incr,
                         new_version=version_a_incr_str)

        # add event c to version b, run b
        buffer.put_event(nfa_name=NFA_NAME_B,
                         run_id=run_id_b,
                         version=version_b.get_version_as_str(),
                         state_label=LABEL_LAYER_C,
                         event=event_c)

        # should only return events associated with version a and incr
        history_1 = buffer.get_all_events(
            nfa_name=NFA_NAME_A,
            run_id=run_id_a_incr,
            version=version_a)

        self.assertDictEqual(history_1.events, {
            LABEL_LAYER_A: [event_a],
            LABEL_LAYER_B: [event_b]
        })

        # should only return events associated with version 2 and run 2
        history_2 = buffer.get_all_events(
            nfa_name=NFA_NAME_B,
            run_id=run_id_b,
            version=version_b)

        self.assertDictEqual(history_2.events, {
            LABEL_LAYER_C: [event_c]
        })

    def test_remove_version_1_nfa_2_versions_1_event(self):
        buffer = SharedVersionedMatchBuffer()

        # two runs for the same nfa
        run_id_a = generate_unique_string()
        run_id_b = generate_unique_string()

        # version for each run
        version_a = RunVersion()
        version_a.add_level(run_id_a)
        version_a_str = version_a.get_version_as_str()

        version_b = RunVersion()
        version_b.add_level(run_id_b)
        version_b_str = version_b.get_version_as_str()

        # put event for run a
        buffer.put_event(nfa_name=NFA_NAME_A,
                         run_id=run_id_a,
                         version=version_a_str,
                         state_label=LABEL_LAYER_B,
                         event=event_a)

        # match event for event a, run a
        match_event = buffer._eve[NFA_NAME_A][LABEL_LAYER_B][event_a.id]
        self.assertIsNotNone(match_event)
        self.assertEqual(event_a, match_event.event)
        self.assertTrue(version_a_str in match_event.next_ids)

        # put event for run b
        buffer.put_event(nfa_name=NFA_NAME_A,
                         run_id=run_id_b,
                         version=version_b_str,
                         state_label=LABEL_LAYER_B,
                         event=event_a)

        # run b in same match event
        self.assertTrue(version_b_str in match_event.next_ids)

        # remove version a, match event should remain for version b
        buffer.remove_version(nfa_name=NFA_NAME_A, version=version_a_str)

        match_event = buffer._eve[NFA_NAME_A][LABEL_LAYER_B][event_a.id]
        self.assertIsNotNone(match_event)
        self.assertFalse(version_a_str in match_event.next_ids)
        self.assertTrue(version_b_str in match_event.next_ids)

        # remove version b, match event should be removed from the buffer
        buffer.remove_version(nfa_name=NFA_NAME_A, version=version_b_str)

        with self.assertRaises(KeyError):
            match_event = buffer._eve[NFA_NAME_A][LABEL_LAYER_B][event_a.id]
        self.assertFalse(version_b_str in match_event.next_ids)

    def test_to_dict_1_nfa_1_version_3_events_3_labels(self):
        buffer = SharedVersionedMatchBuffer()
        run_id_a = generate_unique_string()

        version_a = RunVersion()
        version_a.add_level(run_id_a)
        version_a_str = version_a.get_version_as_str()

        # add three events to buffer for version a, run a
        buffer.put_event(nfa_name=NFA_NAME_A,
                         run_id=run_id_a,
                         version=version_a_str,
                         state_label=LABEL_LAYER_A,
                         event=event_a)

        buffer.put_event(nfa_name=NFA_NAME_A,
                         run_id=run_id_a,
                         version=version_a_str,
                         state_label=LABEL_LAYER_B,
                         event=event_b)

        buffer.put_event(nfa_name=NFA_NAME_A,
                         run_id=run_id_a,
                         version=version_a_str,
                         state_label=LABEL_LAYER_C,
                         event=event_c)

        # check that it is a dict type
        d = buffer.to_dict()
        self.assertIsInstance(d, dict)

        events = d[SharedVersionedMatchBuffer.EVENTS]
        last = d[SharedVersionedMatchBuffer.LAST]
        labels = []

        # check events
        for event in events:
            self.assertEqual(NFA_NAME_A,
                             event[SharedVersionedMatchBuffer.NFA_NAME])

            # check that the right event is paired with its label
            match_ev = event[SharedVersionedMatchBuffer.MATCH_EVENT]

            # check label
            label = match_ev[MatchEvent.LABEL]
            self.assertTrue((label == LABEL_LAYER_A or
                             label == LABEL_LAYER_B or
                             label == LABEL_LAYER_C) and label not in labels)
            labels.append(label)

            if label == LABEL_LAYER_A:
                self.assertDictEqual(event_a.to_dict(),
                                     match_ev[MatchEvent.EVENT])

            elif label == LABEL_LAYER_B:
                self.assertDictEqual(event_b.to_dict(),
                                     match_ev[MatchEvent.EVENT])

            elif label == LABEL_LAYER_C:
                self.assertDictEqual(event_c.to_dict(),
                                     match_ev[MatchEvent.EVENT])

        match_ev_ids = []

        # check last event
        for event in last:
            self.assertEqual(NFA_NAME_A,
                             event[SharedVersionedMatchBuffer.NFA_NAME])
            self.assertEqual(run_id_a,
                             event[SharedVersionedMatchBuffer.RUN_ID])
            self.assertEqual(version_a_str,
                             event[SharedVersionedMatchBuffer.VERSION])

            match_ev_id = event[SharedVersionedMatchBuffer.EVENT_ID]
            self.assertTrue(match_ev_id not in match_ev_ids)
            match_ev_ids.append(match_ev_id)
