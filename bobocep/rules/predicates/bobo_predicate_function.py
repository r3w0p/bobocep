from inspect import isfunction, signature
from typing import Callable, List

from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.predicates.bobo_predicate import BoboPredicate


class BoboPredicateFunction(BoboPredicate):
    """A predicate that evaluates using a custom function.

    :param function: A callable function that is used to evaluate the
                     predicate. It must have exactly 3 parameters in its
                     signature and return a bool response.
    :type function: Callable

    :raises RuntimeError: Callable is not a function.
    :raises RuntimeError: Callable does not have exactly two parameters in its
                          signature.
    """

    PARAMETERS = 3

    def __init__(self, function: Callable) -> None:
        super().__init__()

        if not isfunction(function):
            raise RuntimeError("Callable must be a function, found {}."
                               .format(type(function)))

        if (len(signature(function).parameters)) != self.PARAMETERS:
            raise RuntimeError("Callable must have exactly {} parameters "
                               "in its signature.".format(self.PARAMETERS))

        self.function = function

    def evaluate(self,
                 event: BoboEvent,
                 history: BoboHistory,
                 recents: List[CompositeEvent]) -> bool:
        return self.function(event, history, recents)
