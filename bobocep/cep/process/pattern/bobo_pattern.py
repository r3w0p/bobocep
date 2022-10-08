# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from typing import Tuple, List

from bobocep.cep.process.pattern.bobo_pattern_block import BoboPatternBlock
from bobocep.cep.process.pattern.bobo_pattern_error import BoboPatternError
from bobocep.cep.process.pattern.predicate.bobo_predicate import BoboPredicate


class BoboPattern:
    """A pattern."""

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

        self.name: str = name
        self.blocks: Tuple[BoboPatternBlock, ...] = tuple(blocks)
        self.preconditions: Tuple[BoboPredicate, ...] = tuple(preconditions)
        self.haltconditions: Tuple[BoboPredicate, ...] = tuple(haltconditions)
