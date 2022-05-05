# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from typing import List

from dpcontracts import require, ensure

from bobocep.pattern.bobo_pattern import BoboPattern
from bobocep.pattern.bobo_pattern_block import BoboPatternBlock
from bobocep.predicate.bobo_predicate import BoboPredicate


class BoboPatternBuilder:
    """A pattern builder."""

    def __init__(self):
        super().__init__()

        self._blocks = []
        self._preconditions = []
        self._haltconditions = []

    @require("'name' must be an instance of str",
             lambda args: isinstance(args.name, str))
    @require("'name' must have a length greater than 0",
             lambda args: len(args.name) > 0)
    @ensure("result must be an instance of BoboPattern",
            lambda args, result: isinstance(result, BoboPattern))
    def generate(self, name: str) -> BoboPattern:
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
