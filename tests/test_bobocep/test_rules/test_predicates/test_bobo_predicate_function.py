import unittest

from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.rules.predicates.bobo_predicate_function import \
    BoboPredicateFunction


def valid_function(event: BoboEvent, history: BoboHistory) -> bool:
    return event.data == "1"


def invalid_function_no_params() -> bool:
    return True


def invalid_function_too_many_params(one, two, three) -> bool:
    return True


def invalid_function_too_few_params(one) -> bool:
    return True


class TestBoboPredicateFunction(unittest.TestCase):

    def test_valid_function(self):
        f = BoboPredicateFunction(valid_function)

        event = PrimitiveEvent(EpochNSClock.generate_timestamp(), "1")
        history = BoboHistory()

        self.assertTrue(f.evaluate(event, history))

    def test_invalid_not_callable(self):
        with self.assertRaises(RuntimeError):
            BoboPredicateFunction(123)

    def test_invalid_function_no_params(self):
        with self.assertRaises(RuntimeError):
            BoboPredicateFunction(invalid_function_no_params)

    def test_invalid_function_too_many_params(self):
        with self.assertRaises(RuntimeError):
            BoboPredicateFunction(invalid_function_too_many_params)

    def test_invalid_function_too_few_params(self):
        with self.assertRaises(RuntimeError):
            BoboPredicateFunction(invalid_function_too_few_params)
