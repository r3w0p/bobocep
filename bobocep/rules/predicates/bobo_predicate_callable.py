from inspect import isfunction, signature, ismethod
from types import MethodType
from typing import Callable, List

from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.predicates.bobo_predicate import BoboPredicate


class BoboPredicateCallable(BoboPredicate):
    """A predicate that evaluates using a custom function or method.

    :param call: A callable function that is used to evaluate the
                 predicate. It must have exactly 3 parameters in its
                 signature and return a bool response.
    :type call: Callable

    :raises RuntimeError: Callable is not a function or method.
    :raises RuntimeError: Callable does not have exactly 3 parameters
                          in its signature.
    """

    PARAMETERS = 3

    def __init__(self, call: Callable) -> None:
        super().__init__()

        if not (isfunction(call) or ismethod(call)):
            raise RuntimeError("Callable must be a function or method, "
                               "found {}.".format(type(call)))

        if (len(signature(call).parameters)) != self.PARAMETERS:
            raise RuntimeError("Callable must have exactly {} parameters "
                               "in its signature.".format(self.PARAMETERS))

        self._call = call
        self._obj = call.__self__ if isinstance(call, MethodType) else None

    def evaluate(self,
                 event: BoboEvent,
                 history: BoboHistory,
                 recent: List[BoboEvent]) -> bool:
        return self._call(event, history, recent)
