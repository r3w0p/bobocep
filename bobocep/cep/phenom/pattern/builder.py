# Copyright (c) 2019-2024 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Builders to assist in generating a pattern.
"""
import typing
from typing import List, Union, Callable

from bobocep.cep.phenom.pattern.pattern import BoboPatternBlock, \
    BoboPattern, BoboPatternError
from bobocep.cep.phenom.pattern.predicate import BoboPredicate, \
    BoboPredicateCall

_EXC_NAME_LEN = "name must have a length greater than 0"


# Decorator "@typing.no_type_check" is used to suppress a mypy issue regarding
# the use of "Union[BoboPredicate, Callable]" for predicate parameters.
# This may have the unintended side effect of suppressing actual typing issues
# present in the methods.


class BoboPatternBuilderError(BoboPatternError):
    """
    A pattern builder error.
    """


class BoboPatternBuilder:
    """
    A pattern builder.
    """

    def __init__(self, name: str, singleton: bool = False):
        """
        :param name: Pattern name.
        """

        if len(name) == 0:
            raise BoboPatternBuilderError(_EXC_NAME_LEN)

        self._name: str = name
        self._singleton: bool = singleton

        self._blocks: List[BoboPatternBlock] = []
        self._preconditions: List[BoboPredicate] = []
        self._haltconditions: List[BoboPredicate] = []

    def generate(self) -> BoboPattern:
        """
        Generates a BoboPattern instance with the configuration specified
        in the builder.

        :return: A BoboPattern instance.
        """

        return BoboPattern(
            name=self._name,
            blocks=self._blocks,
            preconditions=self._preconditions,
            haltconditions=self._haltconditions,
            singleton=self._singleton
        )

    @typing.no_type_check
    def next(self,
             predicate: Union[BoboPredicate, Callable],
             group: str = "",
             times: int = 1,
             loop: bool = False) -> 'BoboPatternBuilder':
        """
        Adds a block with strict contiguity.

        :param predicate: Block predicate. If a Callable is provided, it will
            be wrapped in a BoboPredicateCall instance.
        :param group: Block group.
        :param times: Number of times to add this block to the pattern,
            in sequence.
        :param loop: If `True`, the block loops back onto itself (making it
            non-deterministic). If `False`, the block remains deterministic.

        :return: The BoboPatternBuilder instance that made the function call.
        """

        if isinstance(predicate, Callable):
            predicate = BoboPredicateCall(call=predicate)

        for _ in range(max(times, 1)):
            self._blocks.append(BoboPatternBlock(
                predicates=[predicate],
                group=group,
                strict=True,
                loop=loop,
                negated=False,
                optional=False))
        return self

    @typing.no_type_check
    def not_next(self,
                 predicate: Union[BoboPredicate, Callable],
                 group: str = "",
                 times: int = 1) -> 'BoboPatternBuilder':
        """
        Adds a negated block with strict contiguity.

        :param predicate: Block predicate. If a Callable is provided, it will
            be wrapped in a BoboPredicateCall instance.
        :param group: Block group.
        :param times: Number of times to add this block to the pattern,
            in sequence.

        :return: The BoboPatternBuilder instance that made the function call.
        """

        if isinstance(predicate, Callable):
            predicate = BoboPredicateCall(call=predicate)

        for _ in range(max(times, 1)):
            self._blocks.append(BoboPatternBlock(
                predicates=[predicate],
                group=group,
                strict=True,
                loop=False,
                negated=True,
                optional=False))
        return self

    @typing.no_type_check
    def followed_by(
            self,
            predicate: Union[BoboPredicate, Callable],
            group: str = "",
            times: int = 1,
            loop: bool = False,
            optional: bool = False) -> 'BoboPatternBuilder':
        """
        Adds a block with relaxed contiguity.

        :param predicate: Block predicate. If a Callable is provided, it will
            be wrapped in a BoboPredicateCall instance.
        :param group: Block group.
        :param times: Number of times to add this block to the pattern,
            in sequence.
        :param loop: If `True`, the block loops back onto itself.
        :param optional: If `True`, the block is optional.

        :return: The BoboPatternBuilder instance that made the function call.
        """

        if isinstance(predicate, Callable):
            predicate = BoboPredicateCall(call=predicate)

        for _ in range(max(times, 1)):
            self._blocks.append(BoboPatternBlock(
                predicates=[predicate],
                group=group,
                strict=False,
                loop=loop,
                negated=False,
                optional=optional))
        return self

    @typing.no_type_check
    def not_followed_by(
            self,
            predicate: Union[BoboPredicate, Callable],
            group: str = "",
            times: int = 1) -> 'BoboPatternBuilder':
        """
        Adds a negated block with relaxed contiguity.

        :param predicate: Block predicate. If a Callable is provided, it will
            be wrapped in a BoboPredicateCall instance.
        :param group: Block group.
        :param times: Number of times to add this block to the pattern,
            in sequence.

        :return: The BoboPatternBuilder instance that made the function call.
        """

        if isinstance(predicate, Callable):
            predicate = BoboPredicateCall(call=predicate)

        for _ in range(max(times, 1)):
            self._blocks.append(BoboPatternBlock(
                predicates=[predicate],
                group=group,
                strict=False,
                loop=False,
                negated=True,
                optional=False))
        return self

    @typing.no_type_check
    def followed_by_any(
            self,
            predicates: List[Union[BoboPredicate, Callable]],
            group: str = "",
            times: int = 1,
            loop: bool = False,
            optional: bool = False) -> 'BoboPatternBuilder':
        """
        Adds multiple blocks with non-deterministic relaxed contiguity.

        :param predicates: Predicates, one per block. Any Callable types in
            the list will be wrapped in their own BoboPredicateCall instance.
        :param group: Group name for all blocks.
        :param times: Number of times to add these blocks to the pattern,
            in sequence.
        :param loop: If `True`, the blocks loop back onto themselves.
        :param optional: If `True`, the blocks are optional.

        :return: The BoboPatternBuilder instance that made the function call.
        """

        for i in range(len(predicates)):
            if isinstance(predicates[i], Callable):
                predicates[i] = BoboPredicateCall(
                    call=predicates[i])

        for _ in range(max(times, 1)):
            self._blocks.append(BoboPatternBlock(
                predicates=predicates,
                group=group,
                strict=False,
                loop=loop,
                negated=False,
                optional=optional))
        return self

    @typing.no_type_check
    def not_followed_by_any(
            self,
            predicates: List[Union[BoboPredicate, Callable]],
            group: str = "",
            times: int = 1) -> 'BoboPatternBuilder':
        """
        Adds multiple negated blocks with non-deterministic relaxed contiguity.

        :param predicates: Predicates, one per block. Any Callable types in
            the list will be wrapped in their own BoboPredicateCall instance.
        :param group: Group name for all blocks.
        :param times: Number of times to add these blocks to the pattern,
            in sequence.

        :return: The BoboPatternBuilder instance that made the function call.
        """

        for i in range(len(predicates)):
            if isinstance(predicates[i], Callable):
                predicates[i] = BoboPredicateCall(
                    call=predicates[i])

        for _ in range(max(times, 1)):
            self._blocks.append(BoboPatternBlock(
                predicates=predicates,
                group=group,
                strict=False,
                loop=False,
                negated=True,
                optional=False))
        return self

    @typing.no_type_check
    def precondition(
            self, predicate: Union[BoboPredicate, Callable]) \
            -> 'BoboPatternBuilder':
        """
        Adds a precondition.

        :param predicate: The precondition predicate.
            If a Callable is provided, it will be wrapped in a
            BoboPredicateCall instance.

        :return: The BoboPatternBuilder instance that made the function call.
        """

        if isinstance(predicate, Callable):
            predicate = BoboPredicateCall(call=predicate)

        self._preconditions.append(predicate)
        return self

    @typing.no_type_check
    def haltcondition(
            self, predicate: Union[BoboPredicate, Callable]) \
            -> 'BoboPatternBuilder':
        """
        Adds a haltcondition.

        :param predicate: The haltcondition predicate.
            If a Callable is provided, it will be wrapped in a
            BoboPredicateCall instance.

        :return: The BoboPatternBuilder instance that made the function call.
        """

        if isinstance(predicate, Callable):
            predicate = BoboPredicateCall(call=predicate)

        self._haltconditions.append(predicate)
        return self
