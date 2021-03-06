import unittest
from time import sleep
from typing import List

from bobocep.decider.buffers.shared_versioned_match_buffer import \
    SharedVersionedMatchBuffer
from bobocep.decider.handlers.bobo_nfa_handler import BoboNFAHandler
from bobocep.decider.handlers.nfa_handler_subscriber import \
    INFAHandlerSubscriber
from bobocep.decider.runs.bobo_run import BoboRun
from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.bobo_rule_builder import BoboRuleBuilder
from bobocep.rules.events.action_event import ActionEvent
from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.rules.nfas.patterns.bobo_pattern import BoboPattern
from bobocep.rules.predicates.bobo_predicate_callable import \
    BoboPredicateCallable

EVENT_NAME_A = "event_name_a"
EVENT_NAME_B = "event_name_b"

NFA_NAME_A = "NFA_NAME_A"
NFA_NAME_INVALID = "NFA_NAME_INVALID"

RUN_ID_INVALID = "run_id_invalid"

LABEL_LAYER_A = 'layer_a'
LABEL_LAYER_B = 'layer_b'
LABEL_LAYER_B_C = 'layer_b_c'
LABEL_LAYER_C = 'layer_c'
LABEL_LAYER_D = 'layer_d'

STATE_NAME_A = "state_a"
STATE_NAME_B = "state_b"
STATE_NAME_C = "state_c"
STATE_NAME_D = "state_d"
STATE_NAME_INVALID = "state_invalid"

KEY_A = "key_a"
VALUE_A = "value_a"
VALUE_B = "value_b"
VALUE_C = "value_c"
VALUE_D = "value_d"
VALUE_E = "value_e"


def predicate_key_a_value_a(event: BoboEvent,
                            history: BoboHistory,
                            recent: List[BoboEvent]):
    return event.data[KEY_A] == VALUE_A


def predicate_key_a_value_b(event: BoboEvent,
                            history: BoboHistory,
                            recent: List[BoboEvent]):
    return event.data[KEY_A] == VALUE_B


def predicate_key_a_value_c(event: BoboEvent,
                            history: BoboHistory,
                            recent: List[BoboEvent]):
    return event.data[KEY_A] == VALUE_C


def predicate_key_a_value_d(event: BoboEvent,
                            history: BoboHistory,
                            recent: List[BoboEvent]):
    return event.data[KEY_A] == VALUE_D


event_a = PrimitiveEvent(
    timestamp=EpochNSClock.generate_timestamp(),
    data={KEY_A: VALUE_A})

event_b = PrimitiveEvent(
    timestamp=EpochNSClock.generate_timestamp(),
    data={KEY_A: VALUE_B})

event_c = PrimitiveEvent(
    timestamp=EpochNSClock.generate_timestamp(),
    data={KEY_A: VALUE_C})

event_d = PrimitiveEvent(
    timestamp=EpochNSClock.generate_timestamp(),
    data={KEY_A: VALUE_D})

event_e = PrimitiveEvent(
    timestamp=EpochNSClock.generate_timestamp(),
    data={KEY_A: VALUE_E})

pattern_relaxed = BoboPattern() \
    .followed_by(LABEL_LAYER_A,
                 BoboPredicateCallable(predicate_key_a_value_a)) \
    .followed_by(LABEL_LAYER_B,
                 BoboPredicateCallable(predicate_key_a_value_b)) \
    .followed_by(LABEL_LAYER_C,
                 BoboPredicateCallable(predicate_key_a_value_c)) \
    .followed_by(LABEL_LAYER_D,
                 BoboPredicateCallable(predicate_key_a_value_d))


def handler_setup(nfa_name, pattern, max_recent: int = 1):
    buffer = SharedVersionedMatchBuffer()
    nfa = BoboRuleBuilder.nfa(
        name_nfa=nfa_name,
        pattern=pattern)
    handler = BoboNFAHandler(
        nfa=nfa,
        buffer=buffer,
        max_recent=max_recent)
    handlersub = NFAHandlerSubscriber()
    handler.subscribe(handlersub)

    return nfa, buffer, handler, handlersub


def state_from_layer(nfa, label):
    return nfa.states[list(filter(
        lambda x: x.startswith(label), nfa.states.keys()))[0]]


class StubPredicateClass:

    def __init__(self) -> None:
        super().__init__()

    def predicate_true_1(self,
                         event: BoboEvent,
                         history: BoboHistory,
                         recents: List[BoboEvent]):
        return True

    def predicate_true_2(self,
                         event: BoboEvent,
                         history: BoboHistory,
                         recents: List[BoboEvent]):
        return True

    def predicate_true_3(self,
                         event: BoboEvent,
                         history: BoboHistory,
                         recents: List[BoboEvent]):
        return True


class NFAHandlerSubscriber(INFAHandlerSubscriber):

    def __init__(self) -> None:
        super().__init__()

        self.transition = []
        self.clone = []
        self.final = []
        self.final_history = []
        self.halt = []

    def on_handler_transition(self,
                              nfa_name: str,
                              run_id: str,
                              state_name_from: str,
                              state_name_to: str,
                              event: BoboEvent):
        self.transition.append(run_id)

    def on_handler_clone(self,
                         nfa_name: str,
                         run_id: str,
                         state_name: str,
                         event: BoboEvent):
        self.clone.append(run_id)

    def on_handler_final(self,
                         nfa_name: str,
                         run_id: str,
                         event: CompositeEvent):
        self.final.append(run_id)
        self.final_history.append(event.history)

    def on_handler_halt(self,
                        nfa_name: str,
                        run_id: str):
        self.halt.append(run_id)


class TestBoboNFAHandler(unittest.TestCase):

    def test_subscribe_unsubscribe(self):
        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_relaxed)

        # subscribed
        handler.process(event_a)
        handler.process(event_b)
        handler.process(event_c)
        handler.process(event_d)

        self.assertEqual(len(handlersub.final), 1)

        # unsubscribed
        handler.unsubscribe(handlersub)

        handler.process(event_a)
        handler.process(event_b)
        handler.process(event_c)
        handler.process(event_d)

        self.assertEqual(len(handlersub.final), 1)

    def test_add_recent(self):
        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_relaxed,
            max_recent=2)

        p_event = PrimitiveEvent(
            timestamp=EpochNSClock.generate_timestamp(),
            data={}
        )
        sleep(0.1)
        c_event = CompositeEvent(
            timestamp=EpochNSClock.generate_timestamp(),
            name=EVENT_NAME_A,
            history=BoboHistory(),
            data={}
        )
        sleep(0.1)
        a_event = ActionEvent(
            timestamp=EpochNSClock.generate_timestamp(),
            name=EVENT_NAME_B,
            success=True,
            for_event=c_event
        )

        handler.add_recent(p_event)
        handler.add_recent(c_event)

        self.assertTrue(p_event in handler._recent)
        self.assertTrue(c_event in handler._recent)

        handler.add_recent(a_event)

        self.assertFalse(p_event in handler._recent)
        self.assertTrue(c_event in handler._recent)
        self.assertTrue(a_event in handler._recent)

    def test_to_dict(self):
        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_relaxed,
            max_recent=2)

        run_a = BoboRun(buffer=buffer, nfa=nfa, event=event_a)
        handler.add_run(run_a)

        run_a_dict = run_a.to_dict()
        buffer_dict = buffer.to_dict()

        self.assertDictEqual(handler.to_dict(), {
            BoboNFAHandler.NFA_NAME: nfa.name,
            BoboNFAHandler.BUFFER: buffer_dict,
            BoboNFAHandler.RUNS: [run_a_dict]
        })

    def test_add_then_remove_run_no_halt_no_notify(self):
        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_relaxed)

        run_a = BoboRun(buffer=buffer, nfa=nfa, event=event_a)

        # add run
        handler.add_run(run_a)
        self.assertDictEqual(handler.runs, {
            run_a.id: run_a
        })

        # remove run
        handler.remove_run(run_a.id, halt=False, notify=False)

        self.assertDictEqual(handler.runs, {})
        self.assertFalse(run_a.is_halted())
        self.assertListEqual([], handlersub.halt)

    def test_add_then_remove_run_halt_notify(self):
        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_relaxed)

        run_a = BoboRun(buffer=buffer, nfa=nfa, event=event_a)

        # add run
        handler.add_run(run_a)
        self.assertDictEqual(handler.runs, {
            run_a.id: run_a
        })

        # remove run
        handler.remove_run(run_a.id, halt=True, notify=True)

        self.assertDictEqual(handler.runs, {})
        self.assertTrue(run_a.is_halted())
        self.assertListEqual([run_a.id], handlersub.halt)

    def test_add_then_clear_runs_no_halt_no_notify(self):
        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_relaxed)

        run_a = BoboRun(buffer=buffer, nfa=nfa, event=event_a)
        run_b = BoboRun(buffer=buffer, nfa=nfa, event=event_b)
        run_c = BoboRun(buffer=buffer, nfa=nfa, event=event_c)

        # add runs
        handler.add_run(run_a)
        handler.add_run(run_b)
        handler.add_run(run_c)

        self.assertDictEqual(handler.runs, {
            run_a.id: run_a,
            run_b.id: run_b,
            run_c.id: run_c
        })

        # clear runs
        handler.clear_runs(halt=False, notify=False)

        self.assertDictEqual(handler.runs, {})
        self.assertFalse(run_a.is_halted())
        self.assertFalse(run_b.is_halted())
        self.assertFalse(run_c.is_halted())
        self.assertListEqual([], handlersub.halt)

    def test_add_then_clear_runs_halt_notify(self):
        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_relaxed)

        run_a = BoboRun(buffer=buffer, nfa=nfa, event=event_a)
        run_b = BoboRun(buffer=buffer, nfa=nfa, event=event_b)
        run_c = BoboRun(buffer=buffer, nfa=nfa, event=event_c)

        # add runs
        handler.add_run(run_a)
        handler.add_run(run_b)
        handler.add_run(run_c)

        self.assertDictEqual(handler.runs, {
            run_a.id: run_a,
            run_b.id: run_b,
            run_c.id: run_c
        })

        # clear runs
        handler.clear_runs(halt=True, notify=True)

        self.assertDictEqual(handler.runs, {})
        self.assertTrue(run_a.is_halted())
        self.assertTrue(run_b.is_halted())
        self.assertTrue(run_c.is_halted())
        self.assertListEqual(handlersub.halt, [
            run_a.id,
            run_b.id,
            run_c.id
        ])

    def test_duplicate_run_id(self):
        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_relaxed)

        run_id = "abc123"
        run_a = BoboRun(buffer=buffer, nfa=nfa, event=event_a, run_id=run_id)
        run_b = BoboRun(buffer=buffer, nfa=nfa, event=event_b, run_id=run_id)

        self.assertIsNone(handler.add_run(run_a))

        with self.assertRaises(RuntimeError):
            handler.add_run(run_b)

    def test_only_one_state_in_nfa(self):
        pattern_one = BoboPattern().followed_by(
            LABEL_LAYER_A,
            BoboPredicateCallable(predicate_key_a_value_a))

        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_one)

        handler.process(event_a)

        self.assertEqual(len(handlersub.final_history), 1)
        self.assertDictEqual(handlersub.final_history[0].events,
                             {LABEL_LAYER_A: [event_a]})

    def test_deterministic_relaxed_success(self):
        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_relaxed)

        handler.process(event_a)
        handler.process(event_b)
        handler.process(event_c)
        handler.process(event_d)

        self.assertEqual(len(handlersub.final_history), 1)
        self.assertDictEqual(handlersub.final_history[0].events,
                             {LABEL_LAYER_A: [event_a],
                              LABEL_LAYER_B: [event_b],
                              LABEL_LAYER_C: [event_c],
                              LABEL_LAYER_D: [event_d]})

    def test_deterministic_relaxed_optional(self):
        pattern_optional = BoboPattern() \
            .followed_by(LABEL_LAYER_A,
                         BoboPredicateCallable(predicate_key_a_value_a)) \
            .followed_by(LABEL_LAYER_B,
                         BoboPredicateCallable(predicate_key_a_value_b),
                         optional=True) \
            .followed_by(LABEL_LAYER_C,
                         BoboPredicateCallable(predicate_key_a_value_c)) \
            .followed_by(LABEL_LAYER_D,
                         BoboPredicateCallable(predicate_key_a_value_d))

        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_optional)

        handler.process(event_a)
        handler.process(event_c)
        handler.process(event_d)

        self.assertEqual(len(handlersub.final_history), 1)
        self.assertDictEqual(handlersub.final_history[0].events,
                             {LABEL_LAYER_A: [event_a],
                              LABEL_LAYER_C: [event_c],
                              LABEL_LAYER_D: [event_d]})

    def test_deterministic_relaxed_negated_success(self):
        pattern_negated = BoboPattern() \
            .followed_by(LABEL_LAYER_A,
                         BoboPredicateCallable(predicate_key_a_value_a)) \
            .not_followed_by(LABEL_LAYER_B,
                             BoboPredicateCallable(predicate_key_a_value_b)) \
            .followed_by(LABEL_LAYER_C,
                         BoboPredicateCallable(predicate_key_a_value_c)) \
            .followed_by(LABEL_LAYER_D,
                         BoboPredicateCallable(predicate_key_a_value_d))

        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_negated)

        handler.process(event_a)
        handler.process(event_c)
        handler.process(event_d)

        self.assertEqual(len(handlersub.final_history), 1)
        self.assertDictEqual(handlersub.final_history[0].events,
                             {LABEL_LAYER_A: [event_a],
                              LABEL_LAYER_C: [event_c],
                              LABEL_LAYER_D: [event_d]})

    def test_deterministic_relaxed_negated_failure(self):
        pattern_negated = BoboPattern() \
            .followed_by(LABEL_LAYER_A,
                         BoboPredicateCallable(predicate_key_a_value_a)) \
            .not_followed_by(LABEL_LAYER_B,
                             BoboPredicateCallable(predicate_key_a_value_b)) \
            .followed_by(LABEL_LAYER_C,
                         BoboPredicateCallable(predicate_key_a_value_c)) \
            .followed_by(LABEL_LAYER_D,
                         BoboPredicateCallable(predicate_key_a_value_d))

        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_negated)

        handler.process(event_a)
        handler.process(event_b)  # should NOT be followed by this

        self.assertEqual(1, len(handlersub.halt))

    def test_deterministic_strict_success(self):
        pattern_strict = BoboPattern() \
            .next(LABEL_LAYER_A,
                  BoboPredicateCallable(predicate_key_a_value_a)) \
            .next(LABEL_LAYER_B,
                  BoboPredicateCallable(predicate_key_a_value_b)) \
            .next(LABEL_LAYER_C,
                  BoboPredicateCallable(predicate_key_a_value_c)) \
            .next(LABEL_LAYER_D,
                  BoboPredicateCallable(predicate_key_a_value_d))

        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_strict)

        handler.process(event_a)
        handler.process(event_b)
        handler.process(event_c)
        handler.process(event_d)

        self.assertEqual(len(handlersub.final_history), 1)
        self.assertDictEqual(handlersub.final_history[0].events,
                             {LABEL_LAYER_A: [event_a],
                              LABEL_LAYER_B: [event_b],
                              LABEL_LAYER_C: [event_c],
                              LABEL_LAYER_D: [event_d]})

    def test_deterministic_strict_failure(self):
        pattern_strict = BoboPattern() \
            .next(LABEL_LAYER_A,
                  BoboPredicateCallable(predicate_key_a_value_a)) \
            .next(LABEL_LAYER_B,
                  BoboPredicateCallable(predicate_key_a_value_b)) \
            .next(LABEL_LAYER_C,
                  BoboPredicateCallable(predicate_key_a_value_c)) \
            .next(LABEL_LAYER_D,
                  BoboPredicateCallable(predicate_key_a_value_d))

        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_strict)

        handler.process(event_a)
        handler.process(event_e)  # event not in pattern

        self.assertEqual(len(handler.runs.keys()), 0)

    def test_deterministic_strict_negated_success(self):
        pattern_strict_negated = BoboPattern() \
            .next(LABEL_LAYER_A,
                  BoboPredicateCallable(predicate_key_a_value_a)) \
            .not_next(LABEL_LAYER_B,
                      BoboPredicateCallable(predicate_key_a_value_b)) \
            .next(LABEL_LAYER_C,
                  BoboPredicateCallable(predicate_key_a_value_c)) \
            .next(LABEL_LAYER_D,
                  BoboPredicateCallable(predicate_key_a_value_d))

        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_strict_negated)

        handler.process(event_a)
        handler.process(event_c)
        handler.process(event_d)

        self.assertEqual(len(handlersub.final_history), 1)
        self.assertDictEqual(handlersub.final_history[0].events,
                             {LABEL_LAYER_A: [event_a],
                              LABEL_LAYER_C: [event_c],
                              LABEL_LAYER_D: [event_d]})

    def test_deterministic_strict_negated_failure(self):
        pattern_strict_negated = BoboPattern() \
            .next(LABEL_LAYER_A,
                  BoboPredicateCallable(predicate_key_a_value_a)) \
            .not_next(LABEL_LAYER_B,
                      BoboPredicateCallable(predicate_key_a_value_b)) \
            .next(LABEL_LAYER_C,
                  BoboPredicateCallable(predicate_key_a_value_c)) \
            .next(LABEL_LAYER_D,
                  BoboPredicateCallable(predicate_key_a_value_d))

        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_strict_negated)

        handler.process(event_a)
        handler.process(event_e)  # event not in pattern
        handler.process(event_c)
        handler.process(event_d)

        self.assertEqual(len(handlersub.final_history), 0)

    def test_haltconditions(self):
        pattern_haltcond = BoboPattern() \
            .followed_by(LABEL_LAYER_A,
                         BoboPredicateCallable(predicate_key_a_value_a)) \
            .followed_by(LABEL_LAYER_B,
                         BoboPredicateCallable(predicate_key_a_value_b)) \
            .followed_by(LABEL_LAYER_C,
                         BoboPredicateCallable(predicate_key_a_value_c)) \
            .haltcondition(BoboPredicateCallable(predicate_key_a_value_d))

        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_haltcond)

        # haltcondition not triggered, run not halted
        handler.process(event_a)
        handler.process(event_b)
        self.assertEqual(0, len(handlersub.halt))

        # haltcondition triggered, halts run
        handler.process(event_d)
        self.assertEqual(1, len(handlersub.halt))


class TestBoboNFAHandlerNondeterminism(unittest.TestCase):

    def test_nondeterministic_success(self):
        pattern_nondet = BoboPattern() \
            .followed_by(LABEL_LAYER_A,
                         BoboPredicateCallable(predicate_key_a_value_a)) \
            .followed_by_any(LABEL_LAYER_B_C,
                             [BoboPredicateCallable(predicate_key_a_value_b),
                              BoboPredicateCallable(
                                  predicate_key_a_value_c)]) \
            .next(LABEL_LAYER_D,
                  BoboPredicateCallable(predicate_key_a_value_d))

        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_nondet)

        event_d1 = PrimitiveEvent(
            timestamp=EpochNSClock.generate_timestamp(),
            data=event_d.data)

        event_d2 = PrimitiveEvent(
            timestamp=EpochNSClock.generate_timestamp(),
            data=event_d.data)

        handler.process(event_a)
        handler.process(event_b)
        handler.process(event_d1)

        self.assertEqual(len(handlersub.final_history), 1)
        self.assertDictEqual(handlersub.final_history[0].events,
                             {LABEL_LAYER_A: [event_a],
                              LABEL_LAYER_B_C: [event_b],
                              LABEL_LAYER_D: [event_d1]})

        handler.process(event_c)
        handler.process(event_d2)

        self.assertEqual(len(handlersub.final_history), 2)
        self.assertDictEqual(handlersub.final_history[1].events,
                             {LABEL_LAYER_A: [event_a],
                              LABEL_LAYER_B_C: [event_c],
                              LABEL_LAYER_D: [event_d2]})

    def test_nondeterministic_loop_success(self):
        pattern_loop = BoboPattern() \
            .followed_by(LABEL_LAYER_A,
                         BoboPredicateCallable(predicate_key_a_value_a)) \
            .followed_by(LABEL_LAYER_B,
                         BoboPredicateCallable(predicate_key_a_value_b),
                         loop=True) \
            .followed_by(LABEL_LAYER_C,
                         BoboPredicateCallable(predicate_key_a_value_c)) \
            .followed_by(LABEL_LAYER_D,
                         BoboPredicateCallable(predicate_key_a_value_d))

        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_loop)

        event_b1 = PrimitiveEvent(
            timestamp=EpochNSClock.generate_timestamp(),
            data=event_b.data)

        event_b2 = PrimitiveEvent(
            timestamp=EpochNSClock.generate_timestamp(),
            data=event_b.data)

        event_c1 = PrimitiveEvent(
            timestamp=EpochNSClock.generate_timestamp(),
            data=event_c.data)

        event_c2 = PrimitiveEvent(
            timestamp=EpochNSClock.generate_timestamp(),
            data=event_c.data)

        # first run cloned
        handler.process(event_a)
        handler.process(event_b)
        self.assertEqual(1, len(handler.runs.values()))
        run = list(handler.runs.values())[0]

        # first run loops
        handler.process(event_b1)
        self.assertEqual(1, len(handler.runs.values()))

        # second run cloned
        handler.process(event_c1)
        self.assertEqual(2, len(handler.runs.values()))

        # first run increments
        handler.process(event_b2)
        self.assertEqual(2, len(handler.runs.values()))

        # third run cloned
        handler.process(event_c2)
        self.assertEqual(3, len(handler.runs.values()))

        # second and third run reach final state
        handler.process(event_d)
        self.assertEqual(1, len(handler.runs.values()))

        # first run is the only run left
        self.assertEqual(run, list(handler.runs.values())[0])


class TestBoboNFAHandlerTransition(unittest.TestCase):

    def test_force_run_transition(self):
        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_relaxed)

        run_state_a = state_from_layer(nfa=nfa, label=LABEL_LAYER_A)
        run_state_b = state_from_layer(nfa=nfa, label=LABEL_LAYER_B)

        # create a run in its first state
        handler.process(event_a)

        # only one run has been created
        runs = list(handler.runs.values())
        self.assertEqual(1, len(runs))

        run = runs[0]
        self.assertEqual(event_a, run.event)
        self.assertEqual(run_state_a.name, run.current_state.name)

        # force transition to second state
        handler.force_run_transition(
            run_id=run.id,
            state_name_from=run_state_a.name,
            state_name_to=run_state_b.name,
            event=event_b)

        self.assertEqual(event_b, run.event)
        self.assertEqual(run_state_b.name, run.current_state.name)

    def test_force_transition_invalid_run_id(self):
        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_relaxed)

        run_state_a = state_from_layer(nfa=nfa, label=LABEL_LAYER_A)
        run_state_b = state_from_layer(nfa=nfa, label=LABEL_LAYER_B)

        handler.process(event_a)
        run = list(handler.runs.values())[0]

        # state that is in the NFA
        with self.assertRaises(RuntimeError):
            handler.force_run_transition(
                run_id=NFA_NAME_INVALID,
                state_name_from=run_state_a.name,
                state_name_to=run_state_b.name,
                event=event_b)

    def test_force_transition_invalid_from_state(self):
        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_relaxed)

        run_state_b = state_from_layer(nfa=nfa, label=LABEL_LAYER_B)
        run_state_c = state_from_layer(nfa=nfa, label=LABEL_LAYER_C)

        handler.process(event_a)
        run = list(handler.runs.values())[0]

        # from is NOT the current state
        with self.assertRaises(RuntimeError):
            handler.force_run_transition(
                run_id=run.id,
                state_name_from=run_state_b.name,
                state_name_to=run_state_c.name,
                event=event_b)

        # from is NOT a state in the NFA
        with self.assertRaises(RuntimeError):
            handler.force_run_transition(
                run_id=run.id,
                state_name_from=STATE_NAME_INVALID,
                state_name_to=run_state_b.name,
                event=event_b)

    def test_force_transition_invalid_to_state(self):
        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_relaxed)

        run_state_a = state_from_layer(nfa=nfa, label=LABEL_LAYER_A)
        run_state_c = state_from_layer(nfa=nfa, label=LABEL_LAYER_C)

        handler.process(event_a)
        run = list(handler.runs.values())[0]

        # state that is not a transition state
        with self.assertRaises(RuntimeError):
            handler.force_run_transition(
                run_id=run.id,
                state_name_from=run_state_a.name,
                state_name_to=run_state_c.name,
                event=event_b)

        # state that is not in the NFA
        with self.assertRaises(RuntimeError):
            handler.force_run_transition(
                run_id=run.id,
                state_name_from=run_state_a.name,
                state_name_to=STATE_NAME_INVALID,
                event=event_b)

    def test_force_transition_to_final_state(self):
        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_relaxed)

        run_state_c = state_from_layer(nfa=nfa, label=LABEL_LAYER_C)
        run_state_d = state_from_layer(nfa=nfa, label=LABEL_LAYER_D)

        handler.process(event_a)
        handler.process(event_b)
        handler.process(event_c)

        run = list(handler.runs.values())[0]

        handler.force_run_transition(
            run_id=run.id,
            state_name_from=run_state_c.name,
            state_name_to=run_state_d.name,
            event=event_d)

        self.assertTrue(run.is_halted())


class TestBoboNFAHandlerClone(unittest.TestCase):

    def test_force_run_clone(self):
        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_relaxed)

        run_state_a = state_from_layer(nfa=nfa, label=LABEL_LAYER_A)
        run_state_b = state_from_layer(nfa=nfa, label=LABEL_LAYER_B)

        handler.process(event_a)

        # only one run has been created
        runs = list(handler.runs.values())
        self.assertEqual(1, len(runs))

        run = runs[0]
        self.assertEqual(event_a, run.event)
        self.assertEqual(run_state_a.name, run.current_state.name)

        handler.force_run_clone(parent_run_id=run.id,
                                state_name=run_state_b.name,
                                event=event_b)

        self.assertEqual(2, len(handler.runs.values()))

        bothruns = list(handler.runs.values())
        bothruns.remove(run)
        clone_run = bothruns[0]

        self.assertIsNotNone(clone_run)
        self.assertEqual(event_b, clone_run.event)
        self.assertEqual(run_state_b.name, clone_run.current_state.name)

    def test_clone_force_parent_with_no_parent(self):
        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_relaxed)

        handler.process(event_a)
        run = list(handler.runs.values())[0]

        with self.assertRaises(RuntimeError):
            handler.on_run_clone(
                state_name=STATE_NAME_INVALID,
                event=event_a,
                parent_run_id=None,
                force_parent=True,
                notify=True)

    def test_clone_state_not_found(self):
        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_relaxed)

        handler.process(event_a)
        run = list(handler.runs.values())[0]

        with self.assertRaises(RuntimeError):
            handler.on_run_clone(
                state_name=STATE_NAME_INVALID,
                event=event_a,
                parent_run_id=run.id,
                force_parent=False,
                notify=True)


class TestBoboNFAHandlerHalt(unittest.TestCase):

    def test_force_run_halt(self):
        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_relaxed)

        run_state_a = state_from_layer(nfa=nfa, label=LABEL_LAYER_A)
        run_state_b = state_from_layer(nfa=nfa, label=LABEL_LAYER_B)

        handler.process(event_a)

        # only one run has been created
        runs = list(handler.runs.values())
        self.assertEqual(1, len(runs))

        run = runs[0]
        self.assertEqual(event_a, run.event)
        self.assertEqual(run_state_a.name, run.current_state.name)

        handler.process(event_b)

        handler.force_run_halt(run_id=run.id)

        self.assertTrue(run.is_halted())
        self.assertEqual(event_b, run.event)
        self.assertEqual(run_state_b.name, run.current_state.name)

    def test_force_run_halt_invalid_run(self):
        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_relaxed)

        handler.process(event_a)

        with self.assertRaises(RuntimeError):
            handler.force_run_halt(run_id=RUN_ID_INVALID)

    def test_force_run_halt_already_halted(self):
        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_relaxed)

        handler.process(event_a)
        run = list(handler.runs.values())[0]

        # no notification keeps run in handler while halted
        run.set_halt(notify=False)

        with self.assertRaises(RuntimeError):
            handler.force_run_halt(run_id=run.id)


class TestBoboNFAHandlerFinal(unittest.TestCase):

    def test_force_run_final(self):
        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern_relaxed)

        run_state_a = state_from_layer(nfa=nfa, label=LABEL_LAYER_A)

        handler.process(event_a)

        # only one run has been created
        runs = list(handler.runs.values())
        self.assertEqual(1, len(runs))

        run = runs[0]
        self.assertEqual(event_a, run.event)
        self.assertEqual(run_state_a.name, run.current_state.name)

        handler.process(event_b)

        history = BoboHistory()
        handler.force_run_final(run_id=run.id, history=history)

        self.assertTrue(run.is_halted())


class TestPredicateCallable(unittest.TestCase):

    def test_all_callables_method_same_object(self):
        obj = StubPredicateClass()

        pattern = BoboPattern() \
            .followed_by(LABEL_LAYER_A,
                         BoboPredicateCallable(obj.predicate_true_1)) \
            .followed_by(LABEL_LAYER_B,
                         BoboPredicateCallable(obj.predicate_true_2)) \
            .followed_by(LABEL_LAYER_C,
                         BoboPredicateCallable(obj.predicate_true_3))

        nfa, buffer, handler, handlersub = handler_setup(
            nfa_name=NFA_NAME_A,
            pattern=pattern)

        handler.process(event_a)
        handler.process(event_b)
        handler.process(event_c)

        self.assertEqual(1, len(handlersub.final))
