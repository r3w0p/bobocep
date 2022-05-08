# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from inspect import signature
from types import MethodType
from typing import Callable

from bobocep.event.bobo_event import BoboEvent
from bobocep.event.bobo_history import BoboHistory
from bobocep.predicate.bobo_predicate import BoboPredicate
from bobocep.predicate.exception.bobo_predicate_invalid_callable_error import \
    BoboPredicateInvalidCallableError


class BoboPredicateCall(BoboPredicate):
    """A predicate that evaluates using a custom function or method.

    :param call: A callable that is used to evaluate the predicate.
                 It must match the BoboPredicate 'evaluate' method's parameter
                 count and return a bool.
    :type call: Callable
    """

    _EXC_INVALID_CALL = "'call' must have {} parameters, found {}"

    def __init__(self, call: Callable):
        super().__init__()

        len_param_call = len(signature(call).parameters)
        len_param_eval = len(signature(self.evaluate).parameters)

        if len_param_call != len_param_eval:
            raise BoboPredicateInvalidCallableError(
                self._EXC_INVALID_CALL.format(len_param_eval,
                                              len_param_call))

        self._call = call

        # Prevent garbage collection of object if callable is a method.
        self._obj = call.__self__ if isinstance(call, MethodType) else None

    def evaluate(self, event: BoboEvent, history: BoboHistory) -> bool:
        return self._call(event, history)
