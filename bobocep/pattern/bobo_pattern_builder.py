from typing import List

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
             loop: bool = False,
             optional: bool = False) -> 'BoboPatternBuilder':

        for _ in range(max(times, 1)):
            self._blocks.append(BoboPatternBlock(
                group=group,
                predicates=[predicate],
                strict=True,
                loop=loop,
                negated=False,
                optional=optional))
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
                negated=True,
                optional=False))
        return self

    def followed_by(self,
                    group: str,
                    predicate: BoboPredicate,
                    times: int = 1,
                    optional: bool = False) -> 'BoboPatternBuilder':

        for _ in range(max(times, 1)):
            self._blocks.append(BoboPatternBlock(
                group=group,
                predicates=[predicate],
                strict=False,
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
                negated=True,
                optional=False))
        return self

    def followed_by_any(self,
                        group: str,
                        predicates: List[BoboPredicate],
                        times: int = 1,
                        optional: bool = False) -> 'BoboPatternBuilder':

        for _ in range(max(times, 1)):
            self._blocks.append(BoboPatternBlock(
                group=group,
                predicates=predicates,
                strict=False,
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
