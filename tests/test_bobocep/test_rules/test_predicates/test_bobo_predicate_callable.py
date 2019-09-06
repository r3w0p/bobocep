import unittest

from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.rules.predicates.bobo_predicate_callable import \
    BoboPredicateCallable

KEY = "key"
VALUE = "value"
KEY_VALUE = {KEY: VALUE}


def valid_function(e, h, r) -> bool:
    return KEY in e.data.keys() and VALUE in e.data.values()


def invalid_function_no_params() -> bool:
    return True


def invalid_function_too_many_params(one, two, three, four) -> bool:
    return True


def invalid_function_too_few_params(one) -> bool:
    return True


class TestBoboPredicateCallableMethods:

    def __init__(self) -> None:
        super().__init__()

    def valid_method(self, e, h, r) -> bool:
        return KEY in e.data.keys() and VALUE in e.data.values()

    def invalid_method_no_params(self) -> bool:
        return True

    def invalid_method_too_many_params(self, one, two, three, four) -> bool:
        return True

    def invalid_method_too_few_params(self, one) -> bool:
        return True


class TestBoboPredicateCallableOther(unittest.TestCase):

    def test_invalid_not_callable(self):
        with self.assertRaises(RuntimeError):
            # noinspection PyTypeChecker
            BoboPredicateCallable(123)


class TestBoboPredicateCallableFunction(unittest.TestCase):

    def test_valid_function(self):
        f = BoboPredicateCallable(valid_function)
        history = BoboHistory()
        recent = []

        self.assertTrue(f.evaluate(
            event=PrimitiveEvent(
                EpochNSClock.generate_timestamp(),
                KEY_VALUE),
            history=history,
            recent=recent))

    def test_invalid_function_no_params(self):
        with self.assertRaises(RuntimeError):
            BoboPredicateCallable(invalid_function_no_params)

    def test_invalid_function_too_many_params(self):
        with self.assertRaises(RuntimeError):
            BoboPredicateCallable(invalid_function_too_many_params)

    def test_invalid_function_too_few_params(self):
        with self.assertRaises(RuntimeError):
            BoboPredicateCallable(invalid_function_too_few_params)


class TestBoboPredicateCallableMethod(unittest.TestCase):

    def test_valid_method(self):
        obj = TestBoboPredicateCallableMethods()
        f = BoboPredicateCallable(obj.valid_method)
        history = BoboHistory()
        recent = []

        self.assertTrue(f.evaluate(
            event=PrimitiveEvent(
                EpochNSClock.generate_timestamp(),
                KEY_VALUE),
            history=history,
            recent=recent))

    def test_invalid_method_no_params(self):
        with self.assertRaises(RuntimeError):
            obj = TestBoboPredicateCallableMethods()
            BoboPredicateCallable(obj.invalid_method_no_params)

    def test_invalid_method_too_many_params(self):
        with self.assertRaises(RuntimeError):
            obj = TestBoboPredicateCallableMethods()
            BoboPredicateCallable(obj.invalid_method_too_many_params)

    def test_invalid_method_too_few_params(self):
        with self.assertRaises(RuntimeError):
            obj = TestBoboPredicateCallableMethods()
            BoboPredicateCallable(obj.invalid_method_too_few_params)
