# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""Builders to assist in generating a pattern."""

from typing import List

from bobocep import BoboError
from bobocep.cep.phenomenon.pattern import BoboPatternBlock, \
    BoboPattern
from bobocep.cep.phenomenon.pattern.predicate import BoboPredicate


class BoboPatternBuilderError(BoboError):
    """A pattern builder error."""


class BoboPatternBuilder:
    """A pattern builder."""

    _EXC_NAME_LEN = "'name' must have a length greater than 0"

    def __init__(self):
        super().__init__()

        self._blocks: List[BoboPatternBlock] = []
        self._preconditions: List[BoboPredicate] = []
        self._haltconditions: List[BoboPredicate] = []

    def generate(self, name: str) -> BoboPattern:
        if len(name) == 0:
            raise BoboPatternBuilderError(self._EXC_NAME_LEN)

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
        """Adds a precondition.

        :param predicate: The precondition predicate.
        :type predicate: BoboPredicate

        :return: The current BoboPatternBuilder instance.
        :rtype: BoboPatternBuilder
        """

        self._preconditions.append(predicate)
        return self

    def haltcondition(self,
                      predicate: BoboPredicate) -> 'BoboPatternBuilder':
        """Adds a haltcondition.

        :param predicate: The haltcondition predicate.
        :type predicate: BoboPredicate

        :return: The current BoboPatternBuilder instance.
        :rtype: BoboPatternBuilder
        """

        self._haltconditions.append(predicate)
        return self
