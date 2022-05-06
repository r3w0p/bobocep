# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from typing import List

from bobocep.pattern.bobo_pattern_block import BoboPatternBlock
from bobocep.pattern.exception.bobo_pattern_error import BoboPatternError
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

    _EXC_NAME_LEN = "'name' must have a length greater than 0"
    _EXC_BLOCKS_LEN = "'blocks' must have a length greater than 0"
    _EXC_BLOCK_FIRST_NOT_NEG = "first block cannot be negated"
    _EXC_BLOCK_FIRST_NOT_OPT = "first block cannot be optional"
    _EXC_BLOCK_FIRST_NOT_LOOP = "first block cannot loop"
    _EXC_BLOCK_LAST_NOT_NEG = "last block cannot be negated"
    _EXC_BLOCK_LAST_NOT_OPT = "last block cannot be optional"
    _EXC_BLOCK_LAST_NOT_LOOP = "last block cannot loop"

    def __init__(self,
                 name: str,
                 blocks: List[BoboPatternBlock],
                 preconditions: List[BoboPredicate],
                 haltconditions: List[BoboPredicate]):
        super().__init__()

        if len(name) == 0:
            raise BoboPatternError(self._EXC_NAME_LEN)

        if len(blocks) == 0:
            raise BoboPatternError(self._EXC_BLOCKS_LEN)

        if blocks[0].negated:
            raise BoboPatternError(self._EXC_BLOCK_FIRST_NOT_NEG)

        if blocks[0].optional:
            raise BoboPatternError(self._EXC_BLOCK_FIRST_NOT_OPT)

        if blocks[0].loop:
            raise BoboPatternError(self._EXC_BLOCK_FIRST_NOT_LOOP)

        if blocks[-1].negated:
            raise BoboPatternError(self._EXC_BLOCK_LAST_NOT_NEG)

        if blocks[-1].optional:
            raise BoboPatternError(self._EXC_BLOCK_LAST_NOT_OPT)

        if blocks[-1].loop:
            raise BoboPatternError(self._EXC_BLOCK_LAST_NOT_LOOP)

        self.name = name
        self.blocks = tuple(blocks)
        self.preconditions = tuple(preconditions)
        self.haltconditions = tuple(haltconditions)
