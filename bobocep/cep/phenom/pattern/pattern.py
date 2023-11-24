# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
A pattern which models the occurrence of a phenomenon and facilitates the
generating of a complex event.
"""

from typing import Tuple, List

from bobocep import BoboError
from bobocep.cep.phenom.pattern.predicate import BoboPredicate

_EXC_PREDICATES_LEN = "predicates must have a length greater than 0"
_EXC_STRICT_OPT_TRUE = "strict and optional must not both be True"
_EXC_NEG_OR_OPT_LOOP_TRUE = "negated and optional must " \
                            "both be False if loop is True"
_EXC_NEG_AND_OPT_LOOP_FALSE = "negated and optional must not " \
                              "both be True if loop is False"

_EXC_NAME_LEN = "name must have a length greater than 0"
_EXC_BLOCKS_LEN = "blocks must have a length greater than 0"
_EXC_BLOCK_FIRST_NOT_NEG = "first block cannot be negated"
_EXC_BLOCK_FIRST_NOT_OPT = "first block cannot be optional"
_EXC_BLOCK_FIRST_NOT_LOOP = "first block cannot loop"
_EXC_BLOCK_LAST_NOT_NEG = "last block cannot be negated"
_EXC_BLOCK_LAST_NOT_OPT = "last block cannot be optional"
_EXC_BLOCK_LAST_NOT_LOOP = "last block cannot loop"


class BoboPatternError(BoboError):
    """
    A pattern error.
    """


class BoboPatternBlockError(BoboPatternError):
    """
    A pattern block error.
    """


class BoboPatternBlock:
    """
    A pattern block.
    """

    def __init__(self,
                 predicates: List[BoboPredicate],
                 group: str,
                 strict: bool,
                 loop: bool,
                 negated: bool,
                 optional: bool):
        """
        :param predicates: Block predicates.
        :param group: The group with which the block is associated.
            Can be an empty string.
        :param strict: `True` if the block has strict contiguity;
            `False` otherwise.
        :param loop: `True` if the block loops back to itself;
            `False` otherwise.
        :param negated: `True` if the block is negated;
            `False` otherwise.
        :param optional: `True` if the block is optional;
            `False` otherwise.
        """
        super().__init__()

        if len(predicates) == 0:
            raise BoboPatternBlockError(_EXC_PREDICATES_LEN)

        if strict and optional:
            raise BoboPatternBlockError(_EXC_STRICT_OPT_TRUE)

        if loop and (negated or optional):
            raise BoboPatternBlockError(_EXC_NEG_OR_OPT_LOOP_TRUE)

        if (not loop) and (negated and optional):
            raise BoboPatternBlockError(_EXC_NEG_AND_OPT_LOOP_FALSE)

        self._predicates: Tuple[BoboPredicate, ...] = tuple(predicates)
        self._group: str = group
        self._strict: bool = strict
        self._loop: bool = loop
        self._negated: bool = negated
        self._optional: bool = optional

    @property
    def predicates(self) -> Tuple[BoboPredicate, ...]:
        """
        :return: Block predicates.
        """
        return self._predicates

    @property
    def group(self) -> str:
        """
        :return: Block group.
        """
        return self._group

    @property
    def strict(self) -> bool:
        """
        :return: `True` if pattern block has strict contiguity;
            `False` otherwise.
        """
        return self._strict

    @property
    def loop(self) -> bool:
        """
        :return: `True` if pattern block loops;
            `False` otherwise.
        """
        return self._loop

    @property
    def negated(self) -> bool:
        """
        :return: `True` if pattern block is negated;
            `False` otherwise.
        """
        return self._negated

    @property
    def optional(self) -> bool:
        """
        :return: `True` if pattern block is optional;
            `False` otherwise.
        """
        return self._optional


class BoboPattern:
    """
    A pattern that represents a means by which to detect the occurrence of
    some phenomenon.
    """

    def __init__(self,
                 name: str,
                 blocks: List[BoboPatternBlock],
                 preconditions: List[BoboPredicate],
                 haltconditions: List[BoboPredicate],
                 singleton: bool = False):
        """
        :param name: The pattern name.
        :param blocks: The pattern blocks.
        :param preconditions: The pattern preconditions.
        :param haltconditions: The pattern haltconditions.
        :param singleton: If `True`, the pattern can only have one active run
            at a time.
        """
        super().__init__()

        if len(name) == 0:
            raise BoboPatternError(_EXC_NAME_LEN)

        if len(blocks) == 0:
            raise BoboPatternError(_EXC_BLOCKS_LEN)

        if blocks[0].negated:
            raise BoboPatternError(_EXC_BLOCK_FIRST_NOT_NEG)

        if blocks[0].optional:
            raise BoboPatternError(_EXC_BLOCK_FIRST_NOT_OPT)

        if blocks[0].loop:
            raise BoboPatternError(_EXC_BLOCK_FIRST_NOT_LOOP)

        if blocks[-1].negated:
            raise BoboPatternError(_EXC_BLOCK_LAST_NOT_NEG)

        if blocks[-1].optional:
            raise BoboPatternError(_EXC_BLOCK_LAST_NOT_OPT)

        if blocks[-1].loop:
            raise BoboPatternError(_EXC_BLOCK_LAST_NOT_LOOP)

        self._name: str = name
        self._blocks: Tuple[BoboPatternBlock, ...] = tuple(blocks)
        self._preconditions: Tuple[BoboPredicate, ...] = tuple(preconditions)
        self._haltconditions: Tuple[BoboPredicate, ...] = tuple(haltconditions)
        self._singleton: bool = singleton

    @property
    def name(self) -> str:
        """
        :return: Pattern name.
        """
        return self._name

    @property
    def blocks(self) -> Tuple[BoboPatternBlock, ...]:
        """
        :return: Pattern blocks.
        """
        return self._blocks

    @property
    def preconditions(self) -> Tuple[BoboPredicate, ...]:
        """
        :return: Pattern preconditions.
        """
        return self._preconditions

    @property
    def haltconditions(self) -> Tuple[BoboPredicate, ...]:
        """
        :return: Pattern haltconditions.
        """
        return self._haltconditions

    @property
    def singleton(self) -> bool:
        """
        :return: `True` if pattern can only have one active run
            at a time; `False` otherwise.
        """
        return self._singleton
