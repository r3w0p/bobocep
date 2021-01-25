from inspect import isfunction, signature, ismethod
from types import MethodType
from typing import Callable
from dpcontracts import require

from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.bobo_history import BoboHistory
from bobocep.rules.predicates.bobo_predicate import BoboPredicate


class BoboPredicateCallable(BoboPredicate):
    """A predicate that evaluates using a custom function or method.

    :param call: A callable function that is used to evaluate the predicate.
                 It must match the BoboPredicate 'evaluate' method's parameter
                 count and return a bool.
    :type call: Callable

    :raises RuntimeError: Callable is not a function or method.
    :raises RuntimeError: Callable does not have the correct parameter count.
    """

    @require("'call' must be an instance of Callable",
             lambda args: isinstance(args.call, Callable))
    def __init__(self, call: Callable) -> None:
        super().__init__()

        if not (isfunction(call) or ismethod(call)):
            raise RuntimeError(
                "Callable must be a function or method, found {}.".format(
                    type(call)))

        _num_call_params = len(signature(call).parameters)
        _num_predicate_params = len(signature(self.evaluate).parameters)

        if _num_call_params != _num_predicate_params:
            raise RuntimeError(
                "Callable must have exactly {} parameters, found {}.".format(
                    _num_predicate_params, _num_call_params))

        self._call = call
        # Prevent garbage collection of object if callable is a method.
        self._obj = call.__self__ if isinstance(call, MethodType) else None

    def evaluate(self, event: BoboEvent, history: BoboHistory) -> bool:
        return self._call(event, history)
