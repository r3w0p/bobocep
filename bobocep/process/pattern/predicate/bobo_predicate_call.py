# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from inspect import signature
from types import MethodType
from typing import Callable

from bobocep.event.bobo_event import BoboEvent
from bobocep.event.bobo_history import BoboHistory
from bobocep.process.pattern.predicate.bobo_predicate import BoboPredicate
from bobocep.process.pattern.predicate.bobo_predicate_error import \
    BoboPredicateError


class BoboPredicateCall(BoboPredicate):
    """A predicate that evaluates using a custom function or method.

    :param call: A callable that is used to evaluate the predicate.
                 It must match the BoboPredicate 'evaluate' method's parameter
                 count and return a bool.
    :type call: Callable
    """

    _EXC_INVALID_PARAM = "'call' must have {0} parameters, found {1}"
    _LEN_PARAM_CALL = 2

    def __init__(self, call: Callable):
        super().__init__()

        len_param_call = len(signature(call).parameters)

        if len_param_call != self._LEN_PARAM_CALL:
            raise BoboPredicateError(
                self._EXC_INVALID_PARAM.format(
                    self._LEN_PARAM_CALL,
                    len_param_call))

        self._call = call

        # Prevent garbage collection of object if callable is a method.
        self._obj = call.__self__ if isinstance(call, MethodType) else None

    def evaluate(self, event: BoboEvent, history: BoboHistory) -> bool:
        return self._call(event, history)
