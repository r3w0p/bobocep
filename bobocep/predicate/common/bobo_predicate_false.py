from bobocep.events.bobo_event import BoboEvent
from bobocep.events.bobo_history import BoboHistory
from bobocep.predicate.bobo_predicate import BoboPredicate


class BoboPredicateFalse(BoboPredicate):
    """A predicate that evaluates to False."""

    def __init__(self) -> None:
        super().__init__()

    def evaluate(self, event: BoboEvent, history: BoboHistory) -> bool:
        return False
