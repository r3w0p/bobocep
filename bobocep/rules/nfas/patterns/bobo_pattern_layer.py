from typing import List

from bobocep.rules.predicates.bobo_predicate import BoboPredicate


class BoboPatternLayer:
    """A BoboPattern layer, describing the state(s) of a single layer of an
    automaton.

    :param label: The label with which the state(s) will be associated.
    :type label: str

    :param predicates: The predicate(s) that the state(s) will use for
                       evaluation.
    :type predicates: List[BoboPredicate]

    :param times: How many copies of the state(s) to have in sequence,
                  default to 1.
    :type times: int

    :param loop: Whether the state(s) is/are self-looping.
    :type loop: bool

    :param strict: Whether the state(s) has/have strict contiguity.
    :type strict: bool

    :param negated: Whether the state(s) is/are negated.
    :type negated: bool

    :param optional: Whether the state(s) is/are optional.
    :type optional: bool
    """

    def __init__(self,
                 label: str,
                 predicates: List[BoboPredicate],
                 times: int,
                 loop: bool,
                 strict: bool,
                 negated: bool,
                 optional: bool) -> None:
        super().__init__()

        self.label = label
        self.predicates = predicates
        self.times = times
        self.loop = loop
        self.strict = strict
        self.negated = negated
        self.optional = optional
