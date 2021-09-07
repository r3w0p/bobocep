from typing import List

from dpcontracts import require

from bobocep.rules.predicates.bobo_predicate import BoboPredicate


class BoboPatternLayer:
    """A single layer of a pattern.

    :param group: The group with which the state(s) will be associated.
    :type group: str

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

    @require("'group' must be a str",
             lambda args: isinstance(args.group, str))
    @require("'predicates' must be a list of BoboPredicate instances with "
             "length > 0",
             lambda args: isinstance(args.predicates, list) and
                          len(args.predicates) > 0 and
                          all(isinstance(obj, BoboPredicate) for obj in
                              args.predicates))
    @require("'times' must be a int",
             lambda args: isinstance(args.times, int))
    @require("'loop' must be a bool",
             lambda args: isinstance(args.loop, bool))
    @require("'strict' must be a bool",
             lambda args: isinstance(args.strict, bool))
    @require("'negated' must be a bool",
             lambda args: isinstance(args.negated, bool))
    @require("'optional' must be a bool",
             lambda args: isinstance(args.optional, bool))
    def __init__(self,
                 group: str,
                 predicates: List[BoboPredicate],
                 times: int,
                 loop: bool,
                 strict: bool,
                 negated: bool,
                 optional: bool) -> None:
        super().__init__()

        self.group = group
        self.predicates = predicates
        self.times = times
        self.loop = loop
        self.strict = strict
        self.negated = negated
        self.optional = optional
