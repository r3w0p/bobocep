# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from typing import List

from dpcontracts import require

from bobocep.predicate.bobo_predicate import BoboPredicate


class BoboPatternBlock:
    """A pattern block.

    :param group: The group with which the block is associated.
    :type group: str

    :param predicates: The predicate(s) to use for evaluation.
    :type predicates: Tuple[BoboPredicate]

    :param strict: Whether the predicate(s) has/have strict contiguity.
    :type strict: bool

    :param loop: Whether the block loops.
    :type loop: bool

    :param negated: Whether the predicate(s) is/are negated.
    :type negated: bool

    :param optional: Whether the predicate(s) is/are optional.
    :type optional: bool
    """

    # todo cannot be strict and optional?

    @require("'group' must be of type str",
             lambda args: isinstance(args.group, str))
    @require("'group' must have a length greater than 0",
             lambda args: len(args.group) > 0)
    @require("'predicates' must be of type list",
             lambda args: isinstance(args.predicates, list))
    @require("'predicates' must have a length greater than 0",
             lambda args: len(args.predicates) > 0)
    @require("'predicates' must only contain BoboPredicate instances",
             lambda args: all(isinstance(obj, BoboPredicate)
                              for obj in args.predicates))
    @require("'strict' must be of type bool",
             lambda args: isinstance(args.strict, bool))
    @require("'loop' must be of type bool",
             lambda args: isinstance(args.loop, bool))
    @require("'negated' must be of type bool",
             lambda args: isinstance(args.negated, bool))
    @require("'optional' must be of type bool",
             lambda args: isinstance(args.optional, bool))
    @require("'strict' and 'optional' must not both be True",
             lambda args: not (args.strict and args.optional))
    @require("'negated' and 'optional' must both be False if 'loop' is True",
             lambda args: (not args.negated and
                           not args.optional) if args.loop else True)
    @require("'negated' and 'optional' must not both be True "
             "if 'loop' is False",
             lambda args: not (args.negated and args.optional)
             if (not args.loop) else True)
    def __init__(self,
                 group: str,
                 predicates: List[BoboPredicate],
                 strict: bool,
                 loop: bool,
                 negated: bool,
                 optional: bool):
        super().__init__()

        self.group = group
        self.predicates = tuple(predicates)
        self.strict = strict
        self.loop = loop
        self.negated = negated
        self.optional = optional
