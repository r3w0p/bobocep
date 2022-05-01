# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from inspect import signature
from types import MethodType
from typing import Callable

from dpcontracts import require

from bobocep.events.bobo_event import BoboEvent
from bobocep.events.bobo_history import BoboHistory
from bobocep.predicate.bobo_predicate import BoboPredicate


class BoboPredicateCallable(BoboPredicate):
    """A predicate that evaluates using a custom function or method.

    :param call: A callable that is used to evaluate the predicate.
                 It must match the BoboPredicate 'evaluate' method's parameter
                 count and return a bool.
    :type call: Callable

    :raises RuntimeError: Callable is not a function or method.
    :raises RuntimeError: Callable does not have the correct parameter count.
    """

    @require("'call' must be an instance of Callable",
             lambda args: isinstance(args.call, Callable))
    @require("'call' must have an equal number of parameters to the "
             "'evaluate' method from BoboPredicate",
             lambda args: len(signature(args.call).parameters) ==
                          len(signature(args.self.evaluate).parameters))
    def __init__(self, call: Callable):
        super().__init__()

        self._call = call

        # Prevent garbage collection of object if callable is a method.
        self._obj = call.__self__ if isinstance(call, MethodType) else None

    def evaluate(self, event: BoboEvent, history: BoboHistory) -> bool:
        return self._call(event, history)
