import unittest
from typing import List

from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.rules.predicates.bobo_predicate_callable import \
    BoboPredicateCallable
from bobocep.rules.states.bobo_state import BoboState

STATE_A = "state_a"
LABEL_LAYER_A = "LABEL_LAYER_A"

KEY = "key"
VALUE = "value"
KEY_VALUE = {KEY: VALUE}


def predicate_key_value(event: BoboEvent,
                        history: BoboHistory,
                        recent: List[CompositeEvent]):
    return event.data == KEY_VALUE


def predicate_first_history_key_value(event: BoboEvent,
                                      history: BoboHistory,
                                      recent: List[CompositeEvent]):
    return False if history.first is None else history.first.data == KEY_VALUE


class TestBoboState(unittest.TestCase):

    def test_predicate_key_value(self):
        event = PrimitiveEvent(EpochNSClock.generate_timestamp(), KEY_VALUE)
        history = BoboHistory()
        recent = []
        predicate = BoboPredicateCallable(predicate_key_value)
        state = BoboState(STATE_A, LABEL_LAYER_A, predicate)

        self.assertTrue(state.process(event, history, recent))

    def test_first_history_key_value(self):
        event = PrimitiveEvent(EpochNSClock.generate_timestamp(), KEY_VALUE)
        history_event = PrimitiveEvent(EpochNSClock.generate_timestamp(),
                                       KEY_VALUE)
        history = BoboHistory({STATE_A: [history_event]})
        recent = []
        predicate = BoboPredicateCallable(
            predicate_first_history_key_value)
        state = BoboState(STATE_A, LABEL_LAYER_A, predicate)

        self.assertTrue(state.process(event, history, recent))
