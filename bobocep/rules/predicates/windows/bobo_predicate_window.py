from abc import ABC

from bobocep.rules.predicates.bobo_predicate import BoboPredicate


class BoboPredicateWindow(BoboPredicate, ABC):
    """A predicate that evaluates using a time window."""

    def __init__(self) -> None:
        super().__init__()
