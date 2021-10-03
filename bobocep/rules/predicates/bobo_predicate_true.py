from inspect import signature
from types import MethodType
from typing import Callable

from dpcontracts import require

from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.bobo_history import BoboHistory
from bobocep.rules.predicates.bobo_predicate import BoboPredicate


class BoboPredicateTrue(BoboPredicate):
    """A predicate that evaluates to True."""

    def __init__(self) -> None:
        super().__init__()

    def evaluate(self, event: BoboEvent, history: BoboHistory) -> bool:
        return True
