import unittest
from time import sleep
from typing import List

from bobocep.decider.buffers.shared_versioned_match_buffer import \
    SharedVersionedMatchBuffer
from bobocep.decider.handlers.bobo_nfa_handler import BoboNFAHandler
from bobocep.decider.handlers.nfa_handler_subscriber import \
    INFAHandlerSubscriber
from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.bobo_rule_builder import BoboRuleBuilder
from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.rules.nfas.patterns.bobo_pattern import BoboPattern
from bobocep.rules.predicates.bobo_predicate_function import \
    BoboPredicateFunction
from bobocep.rules.predicates.windows.sliding.window_sliding_last import \
    WindowSlidingLast

STATE_A = "state_a"
STATE_B = "state_b"
STATE_C = "state_c"
STATE_D = "state_d"

LABEL_LAYER_A = "LABEL_LAYER_A"
LABEL_LAYER_B = "LABEL_LAYER_B"
LABEL_LAYER_C = "LABEL_LAYER_C"
LABEL_LAYER_D = "LABEL_LAYER_D"

NFA_NAME_A = "NFA_NAME_A"

KEY = "key"
VAL_1 = "1"
VAL_2 = "2"
VAL_3 = "3"
VAL_4 = "4"


def predicate_key_a_value_a(event: BoboEvent,
                            history: BoboHistory,
                            recents: List[CompositeEvent]):
    return event.data[KEY] == VAL_1


def predicate_key_a_value_b(event: BoboEvent,
                            history: BoboHistory,
                            recents: List[CompositeEvent]):
    return event.data[KEY] == VAL_2


def predicate_key_a_value_c(event: BoboEvent,
                            history: BoboHistory,
                            recents: List[CompositeEvent]):
    return event.data[KEY] == VAL_3


def predicate_key_a_value_d(event: BoboEvent,
                            history: BoboHistory,
                            recents: List[CompositeEvent]):
    return event.data[KEY] == VAL_4


class NFAHandlerSubscriber(INFAHandlerSubscriber):

    def __init__(self) -> None:
        super().__init__()

        self.transition = []
        self.clone = []
        self.final = []
        self.final_history = []
        self.halt = []

    def on_handler_transition(self, nfa_name: str, run_id: str,
                              state_name_from: str, state_name_to: str,
                              event: BoboEvent):
        self.transition.append(run_id)

    def on_handler_clone(self, nfa_name: str, run_id: str, state_name: str,
                         event: BoboEvent):
        self.clone.append(run_id)

    def on_handler_final(self, nfa_name: str,
                         run_id: str,
                         event: CompositeEvent):
        self.final.append(run_id)
        self.final_history.append(event.history)

    def on_handler_halt(self, nfa_name: str, run_id: str):
        self.halt.append(run_id)


class TestWindowSlidingLast(unittest.TestCase):

    def test_sliding_last_window_to_final(self):
        timestamp_lower = EpochNSClock.generate_timestamp()
        sleep(0.5)
        timestamp_upper = EpochNSClock.generate_timestamp()
        window_range_ns = timestamp_upper - timestamp_lower

        timestamp_a = timestamp_lower
        timestamp_b = timestamp_a + window_range_ns
        timestamp_c = timestamp_b + window_range_ns

        predicate_a = BoboPredicateFunction(predicate_key_a_value_a)
        predicate_b = BoboPredicateFunction(predicate_key_a_value_b)
        predicate_c = BoboPredicateFunction(predicate_key_a_value_c)
        predicate_first_window = WindowSlidingLast(
            window_range_ns)

        event_a = PrimitiveEvent(timestamp_a, {KEY: VAL_1})
        event_b = PrimitiveEvent(timestamp_b, {KEY: VAL_2})
        event_c = PrimitiveEvent(timestamp_c, {KEY: VAL_3})

        pattern_a = BoboPattern() \
            .followed_by(LABEL_LAYER_A, predicate_a) \
            .followed_by(LABEL_LAYER_B, predicate_b) \
            .followed_by(LABEL_LAYER_C, predicate_c) \
            .precondition(predicate_first_window)

        handler = BoboNFAHandler(
            BoboRuleBuilder.nfa(NFA_NAME_A, pattern_a),
            SharedVersionedMatchBuffer())
        handlersub = NFAHandlerSubscriber()
        handler.subscribe(handlersub)

        handler.process(event_a)
        handler.process(event_b)
        handler.process(event_c)

        self.assertEqual(len(handlersub.final_history), 1)
        self.assertDictEqual(handlersub.final_history[0].events,
                             {LABEL_LAYER_A: [event_a],
                              LABEL_LAYER_B: [event_b],
                              LABEL_LAYER_C: [event_c]})

    def test_sliding_last_window_to_halt(self):
        timestamp_lower = EpochNSClock.generate_timestamp()
        sleep(0.5)
        timestamp_upper = EpochNSClock.generate_timestamp()
        window_range_ns = timestamp_upper - timestamp_lower

        timestamp_a = timestamp_lower
        timestamp_b = timestamp_a + window_range_ns
        timestamp_c = timestamp_b + window_range_ns + 1

        predicate_a = BoboPredicateFunction(predicate_key_a_value_a)
        predicate_b = BoboPredicateFunction(predicate_key_a_value_b)
        predicate_c = BoboPredicateFunction(predicate_key_a_value_c)
        predicate_first_window = WindowSlidingLast(
            window_range_ns)

        event_a = PrimitiveEvent(timestamp_a, {KEY: VAL_1})
        event_b = PrimitiveEvent(timestamp_b, {KEY: VAL_2})
        event_c = PrimitiveEvent(timestamp_c, {KEY: VAL_3})

        pattern_a = BoboPattern() \
            .followed_by(LABEL_LAYER_A, predicate_a) \
            .followed_by(LABEL_LAYER_B, predicate_b) \
            .followed_by(LABEL_LAYER_C, predicate_c) \
            .precondition(predicate_first_window)

        handler = BoboNFAHandler(
            BoboRuleBuilder.nfa(NFA_NAME_A, pattern_a),
            SharedVersionedMatchBuffer())
        handlersub = NFAHandlerSubscriber()
        handler.subscribe(handlersub)

        handler.process(event_a)
        handler.process(event_b)
        handler.process(event_c)

        self.assertEqual(len(handlersub.final), 1)
