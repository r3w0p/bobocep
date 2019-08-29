import unittest

from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.rules.predicates.bobo_predicate_function import \
    BoboPredicateFunction
from bobocep.rules.states.bobo_state import BoboState

STATE_A = "state_a"
LABEL_LAYER_A = "LABEL_LAYER_A"


def predicate_key_a_value_a23(event: BoboEvent, history: BoboHistory):
    return event.data == "123"


def first_history_predicate_key_a_value_d56(event: BoboEvent,
                                            history: BoboHistory):
    return False if history.first is None else history.first.data == "456"


class TestBoboState(unittest.TestCase):

    def test_predicate_key_a_value_a23(self):
        event = PrimitiveEvent(EpochNSClock.generate_timestamp(), "123")
        history = BoboHistory()
        predicate = BoboPredicateFunction(predicate_key_a_value_a23)
        state = BoboState(STATE_A, LABEL_LAYER_A, predicate)

        self.assertTrue(state.process(event, history))

    def test_first_history_predicate_key_a_value_d56(self):
        event = PrimitiveEvent(EpochNSClock.generate_timestamp(), "123")
        history_event = PrimitiveEvent(EpochNSClock.generate_timestamp(),
                                       "456")
        history = BoboHistory({STATE_A: [history_event]})
        predicate = BoboPredicateFunction(
            first_history_predicate_key_a_value_d56)
        state = BoboState(STATE_A, LABEL_LAYER_A, predicate)

        self.assertTrue(state.process(event, history))
