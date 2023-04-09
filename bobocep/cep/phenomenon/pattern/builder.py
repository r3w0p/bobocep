# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Builders to assist in generating a pattern.
"""

from typing import List

from bobocep.cep.phenomenon.pattern.pattern import BoboPatternBlock, \
    BoboPattern, BoboPatternError
from bobocep.cep.phenomenon.pattern.predicate import BoboPredicate

_EXC_NAME_LEN = "name must have a length greater than 0"


class BoboPatternBuilderError(BoboPatternError):
    """
    A pattern builder error.
    """


class BoboPatternBuilder:
    """
    A pattern builder.
    """

    def __init__(self):
        """
        Pattern builder constructor.
        """

        self._blocks: List[BoboPatternBlock] = []
        self._preconditions: List[BoboPredicate] = []
        self._haltconditions: List[BoboPredicate] = []

    def generate(self, name: str) -> BoboPattern:
        """
        Generates a BoboPattern instance with the configuration specified
        in the builder.

        :param name: Name of generated pattern.

        :return: A BoboPattern instance.
        """
        if len(name) == 0:
            raise BoboPatternBuilderError(_EXC_NAME_LEN)

        return BoboPattern(
            name=name,
            blocks=self._blocks,
            preconditions=self._preconditions,
            haltconditions=self._haltconditions
        )

    def next(self,
             group: str,
             predicate: BoboPredicate,
             times: int = 1,
             loop: bool = False) -> 'BoboPatternBuilder':
        """
        Adds a block with strict contiguity.

        :param group: Block group.
        :param predicate: Block predicate.
        :param times: Number of times to add this block to the pattern,
            in sequence.
        :param loop: If `True`, the block loops back onto itself (making it
            non-deterministic). If `False`, the block remains deterministic.

        :return: The BoboPatternBuilder instance that made the function call.
        """

        for _ in range(max(times, 1)):
            self._blocks.append(BoboPatternBlock(
                group=group,
                predicates=[predicate],
                strict=True,
                loop=loop,
                negated=False,
                optional=False))
        return self

    def not_next(self,
                 group: str,
                 predicate: BoboPredicate,
                 times: int = 1) -> 'BoboPatternBuilder':
        """
        Adds a negated block with strict contiguity.

        :param group: Block group.
        :param predicate: Block predicate.
        :param times: Number of times to add this block to the pattern,
            in sequence.

        :return: The BoboPatternBuilder instance that made the function call.
        """

        for _ in range(max(times, 1)):
            self._blocks.append(BoboPatternBlock(
                group=group,
                predicates=[predicate],
                strict=True,
                loop=False,
                negated=True,
                optional=False))
        return self

    def followed_by(self,
                    group: str,
                    predicate: BoboPredicate,
                    times: int = 1,
                    loop: bool = False,
                    optional: bool = False) -> 'BoboPatternBuilder':
        """
        Adds a block with relaxed contiguity.

        :param group: Block group.
        :param predicate: Block predicate.
        :param times: Number of times to add this block to the pattern,
            in sequence.
        :param loop: If `True`, the block loops back onto itself.
        :param optional: If `True`, the block is optional.

        :return: The BoboPatternBuilder instance that made the function call.
        """

        for _ in range(max(times, 1)):
            self._blocks.append(BoboPatternBlock(
                group=group,
                predicates=[predicate],
                strict=False,
                loop=loop,
                negated=False,
                optional=optional))
        return self

    def not_followed_by(self,
                        group: str,
                        predicate: BoboPredicate,
                        times: int = 1) -> 'BoboPatternBuilder':
        """
        Adds a negated block with relaxed contiguity.

        :param group: Block group.
        :param predicate: Block predicate.
        :param times: Number of times to add this block to the pattern,
            in sequence.

        :return: The BoboPatternBuilder instance that made the function call.
        """

        for _ in range(max(times, 1)):
            self._blocks.append(BoboPatternBlock(
                group=group,
                predicates=[predicate],
                strict=False,
                loop=False,
                negated=True,
                optional=False))
        return self

    def followed_by_any(self,
                        group: str,
                        predicates: List[BoboPredicate],
                        times: int = 1,
                        loop: bool = False,
                        optional: bool = False) -> 'BoboPatternBuilder':
        """
        Adds multiple blocks with non-deterministic relaxed contiguity.

        :param group: Group name for all blocks.
        :param predicates: Predicates, one per block.
        :param times: Number of times to add these blocks to the pattern,
            in sequence.
        :param loop: If `True`, the blocks loop back onto themselves.
        :param optional: If `True`, the blocks are optional.

        :return: The BoboPatternBuilder instance that made the function call.
        """

        for _ in range(max(times, 1)):
            self._blocks.append(BoboPatternBlock(
                group=group,
                predicates=predicates,
                strict=False,
                loop=loop,
                negated=False,
                optional=optional))
        return self

    def not_followed_by_any(self,
                            group: str,
                            predicates: List[BoboPredicate],
                            times: int = 1) -> 'BoboPatternBuilder':
        """
        Adds multiple negated blocks with non-deterministic relaxed contiguity.

        :param group: Group name for all blocks.
        :param predicates: Predicates, one per block.
        :param times: Number of times to add these blocks to the pattern,
            in sequence.

        :return: The BoboPatternBuilder instance that made the function call.
        """

        for _ in range(max(times, 1)):
            self._blocks.append(BoboPatternBlock(
                group=group,
                predicates=predicates,
                strict=False,
                loop=False,
                negated=True,
                optional=False))
        return self

    def precondition(self, predicate: BoboPredicate) -> 'BoboPatternBuilder':
        """
        Adds a precondition.

        :param predicate: The precondition predicate.

        :return: The BoboPatternBuilder instance that made the function call.
        """

        self._preconditions.append(predicate)
        return self

    def haltcondition(self,
                      predicate: BoboPredicate) -> 'BoboPatternBuilder':
        """
        Adds a haltcondition.

        :param predicate: The haltcondition predicate.

        :return: The BoboPatternBuilder instance that made the function call.
        """

        self._haltconditions.append(predicate)
        return self
