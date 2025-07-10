# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from typing import Callable, Any, Optional, List

from bobocep.cep.phenomenon.pattern.pattern import BoboPatternBlock, \
    BoboPattern
from bobocep.cep.phenomenon.pattern.predicate import BoboPredicateCall, \
    BoboPredicate


def tc_block(call: Callable = lambda e, h: e.data,
             group: str = "group",
             strict: bool = False,
             loop: bool = False,
             negated: bool = False,
             optional: bool = False) -> BoboPatternBlock:
    return BoboPatternBlock(
        predicates=[BoboPredicateCall(call=call)],
        group=group,
        strict=strict,
        loop=loop,
        negated=negated,
        optional=optional)


def tc_lambda_event_data_equal(d: Any):
    return lambda e, h: e.data == d


def tc_pattern(
        name: str = "pattern",
        data_blocks: Optional[List[Any]] = None,
        data_scon: Optional[List[Any]] = None,
        data_rcon: Optional[List[Any]] = None,
        data_hcon: Optional[List[Any]] = None,
        singleton: bool = False
) -> BoboPattern:
    if data_blocks is None:
        data_blocks = [1]

    if data_scon is None:
        data_scon = []

    if data_rcon is None:
        data_rcon = []

    if data_hcon is None:
        data_hcon = []

    blocks: List[BoboPatternBlock] = []
    for i in range(len(data_blocks)):
        blocks.append(tc_block(
            group="g{}".format(i + 1),
            call=tc_lambda_event_data_equal(data_blocks[i])))

    strict_conditions: List[BoboPredicate] = []
    for i in range(len(data_scon)):
        strict_conditions.append(BoboPredicateCall(
            call=tc_lambda_event_data_equal(data_scon[i])))

    relaxed_conditions: List[BoboPredicate] = []
    for i in range(len(data_scon)):
        relaxed_conditions.append(BoboPredicateCall(
            call=tc_lambda_event_data_equal(data_rcon[i])))

    halt_conditions: List[BoboPredicate] = []
    for i in range(len(data_hcon)):
        halt_conditions.append(BoboPredicateCall(
            call=tc_lambda_event_data_equal(data_hcon[i])))

    return BoboPattern(
        name=name,
        blocks=blocks,
        strict_conditions=strict_conditions,
        relaxed_conditions=relaxed_conditions,
        halt_conditions=halt_conditions,
        singleton=singleton
    )
