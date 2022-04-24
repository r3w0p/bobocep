# Copyright (c) The BoboCEP Authors
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from typing import List

from dpcontracts import require

from bobocep.pattern.bobo_pattern_block import BoboPatternBlock
from bobocep.predicate.bobo_predicate import BoboPredicate


class BoboPattern:
    """A pattern.

    :param name: The name of the pattern.
    :type name: str

    :param blocks: The sequence of blocks that constitute the pattern of
                   behaviour.
    :type blocks: Tuple[BoboPatternBlock]

    :param preconditions: The preconditions that must all equal True for any
                          new event that is being checked against the pattern.
    :type preconditions: Tuple[BoboPredicate]

    :param haltconditions: The haltconditions that must all equal False for any
                           new event that is being checked against the pattern.
    :type haltconditions: Tuple[BoboPredicate]
    """

    @require("'name' must be of type str",
             lambda args: isinstance(args.name, str))
    @require("'name' must have a length greater than 0",
             lambda args: len(args.name) > 0)
    @require("'blocks' must be of type list",
             lambda args: isinstance(args.blocks, list))
    @require("'blocks' must have a length greater than 0",
             lambda args: len(args.blocks) > 0)
    @require("'blocks' must only contain BoboPatternBlock instances",
             lambda args: all(isinstance(obj, BoboPatternBlock)
                              for obj in args.blocks))
    @require("'preconditions' must be of type list",
             lambda args: isinstance(args.preconditions, list))
    @require("'preconditions' must only contain BoboPredicate instances",
             lambda args: all(isinstance(obj, BoboPredicate)
                              for obj in args.preconditions))
    @require("'haltconditions' must be of type list",
             lambda args: isinstance(args.haltconditions, list))
    @require("'haltconditions' must only contain BoboPredicate instances",
             lambda args: all(isinstance(obj, BoboPredicate)
                              for obj in args.haltconditions))
    @require("first block cannot be negated",
             lambda args: not args.blocks[0].negated)
    @require("first block cannot be optional",
             lambda args: not args.blocks[0].optional)
    @require("first block cannot loop",
             lambda args: not args.blocks[0].loop)
    @require("last block cannot be negated",
             lambda args: not args.blocks[-1].negated)
    @require("last block cannot be optional",
             lambda args: not args.blocks[-1].optional)
    @require("last block cannot loop",
             lambda args: not args.blocks[-1].loop)
    def __init__(self,
                 name: str,
                 blocks: List[BoboPatternBlock],
                 preconditions: List[BoboPredicate],
                 haltconditions: List[BoboPredicate]):
        super().__init__()

        self.name = name
        self.blocks = tuple(blocks)
        self.preconditions = tuple(preconditions)
        self.haltconditions = tuple(haltconditions)
