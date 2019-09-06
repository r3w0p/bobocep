import unittest

from bobocep.decider.buffers.shared_versioned_match_buffer import \
    SharedVersionedMatchBuffer
from bobocep.decider.runs.bobo_run import BoboRun
from bobocep.decider.runs.run_subscriber import IRunSubscriber
from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.bobo_rule_builder import BoboRuleBuilder
from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.rules.nfas.patterns.bobo_pattern import BoboPattern
from bobocep.rules.predicates.bobo_predicate_callable import \
    BoboPredicateCallable
from bobocep.rules.states.bobo_state import BoboState

NFA_NAME_A = "NFA_NAME_A"

STATE_NAME_INVALID = "STATE_NAME_INVALID"

LABEL_LAYER_A = 'layer_a'
LABEL_LAYER_B = 'layer_b'
LABEL_LAYER_C = 'layer_c'
LABEL_LAYER_D = 'layer_d'
LABEL_INVALID = 'layer_invalid'

event_a = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())
event_b = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())
event_c = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())

stub_predicate = BoboPredicateCallable(lambda e, h, r: True)

state_invalid = BoboState(
    name=STATE_NAME_INVALID,
    label=LABEL_INVALID,
    predicate=stub_predicate)

stub_pattern = BoboPattern() \
    .followed_by(LABEL_LAYER_A, stub_predicate) \
    .followed_by(LABEL_LAYER_B, stub_predicate) \
    .followed_by(LABEL_LAYER_C, stub_predicate) \
    .followed_by(LABEL_LAYER_D, stub_predicate)


def run_setup(nfa_name: str,
              pattern: BoboPattern,
              start_state: str = None):
    run = BoboRun(
        buffer=SharedVersionedMatchBuffer(),
        nfa=BoboRuleBuilder.nfa(
            name_nfa=nfa_name,
            pattern=pattern),
        event=PrimitiveEvent(
            timestamp=EpochNSClock.generate_timestamp()),
        start_state=start_state)

    runsub = BoboRunSubscriber()
    run.subscribe(runsub)

    return run, runsub


class BoboRunSubscriber(IRunSubscriber):

    def __init__(self) -> None:
        super().__init__()

        self.transition = []
        self.clone = []
        self.final = []
        self.halt = []

    def on_run_transition(self,
                          run_id: str,
                          state_name_from: str,
                          state_name_to: str,
                          event: BoboEvent,
                          notify: bool) -> None:
        self.transition.append(run_id)

    def on_run_clone(self,
                     state_name: str,
                     event: BoboEvent,
                     parent_run_id: str,
                     force_parent: bool,
                     notify: bool) -> None:
        self.clone.append("" if parent_run_id is None else parent_run_id)

    def on_run_final(self,
                     run_id: str,
                     history: BoboHistory,
                     halt: bool,
                     notify: bool) -> None:
        self.final.append(run_id)

    def on_run_halt(self,
                    run_id: str,
                    notify: bool) -> None:
        self.halt.append(run_id)


class TestBoboRun(unittest.TestCase):

    def test_run_from_start_to_final_state(self):
        run, runsub = run_setup(
            nfa_name=NFA_NAME_A,
            pattern=stub_pattern)

        self.assertFalse(run.is_halted())

        run.process(event=event_a, recent=[])
        run.process(event=event_b, recent=[])
        run.process(event=event_c, recent=[])

        self.assertTrue(run.is_halted())

    def test_subscribe_unsubscribe(self):
        run, runsub = run_setup(
            nfa_name=NFA_NAME_A,
            pattern=stub_pattern)

        self.assertEqual(0, len(runsub.transition))
        run.process(event=event_a, recent=[])
        self.assertEqual(1, len(runsub.transition))

        run.unsubscribe(runsub)
        run.process(event=event_b, recent=[])
        self.assertEqual(1, len(runsub.transition))

    def test_halt(self):
        run, runsub = run_setup(
            nfa_name=NFA_NAME_A,
            pattern=stub_pattern)

        self.assertFalse(run.is_halted())
        run.set_halt()

        self.assertTrue(run.is_halted())
        self.assertEqual(1, len(runsub.halt))

    def test_handle_state_not_in_nfa(self):
        run, runsub = run_setup(
            nfa_name=NFA_NAME_A,
            pattern=stub_pattern)

        with self.assertRaises(RuntimeError):
            run._handle_state(
                state=state_invalid,
                event=event_a,
                history=BoboHistory(),
                recent=[])

    def test_proceed_invalid_states(self):
        run, runsub = run_setup(
            nfa_name=NFA_NAME_A,
            pattern=stub_pattern)

        with self.assertRaises(RuntimeError):
            run._proceed(
                event=event_a,
                original_state=state_invalid,
                trans_state=run.nfa.final_state,
                increment=False,
                notify=True)

        with self.assertRaises(RuntimeError):
            run._proceed(
                event=event_a,
                original_state=run.nfa.start_state,
                trans_state=state_invalid,
                increment=False,
                notify=True)

    def test_to_dict(self):
        run, runsub = run_setup(
            nfa_name=NFA_NAME_A,
            pattern=stub_pattern)

        self.assertDictEqual(run.to_dict(), {
            BoboRun.NFA_NAME: run.nfa.name,
            BoboRun.EVENT: run.event.to_dict(),
            BoboRun.START_TIME: run.start_time,
            BoboRun.START_STATE_NAME: run.nfa.start_state.name,
            BoboRun.CURRENT_STATE_NAME: run.nfa.start_state.name,
            BoboRun.RUN_ID: run.id,
            BoboRun.VERSION: run.version._levels,
            BoboRun.HALTED: False,
            BoboRun.LAST_PROCESS_CLONED: False
        })
