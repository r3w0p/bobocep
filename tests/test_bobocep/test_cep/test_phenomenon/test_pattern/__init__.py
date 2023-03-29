# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from typing import Callable, Any, Optional, List

from bobocep.cep.phenomenon.pattern.pattern import BoboPatternBlock, \
    BoboPattern
from bobocep.cep.phenomenon.pattern.predicate import BoboPredicateCall, \
    BoboPredicate


def tc_block(group: str = "group",
             call: Callable = lambda e, h: e.data,
             strict: bool = False,
             loop: bool = False,
             negated: bool = False,
             optional: bool = False) -> BoboPatternBlock:
    return BoboPatternBlock(
        group=group,
        predicates=[BoboPredicateCall(call=call)],
        strict=strict,
        loop=loop,
        negated=negated,
        optional=optional)


def tc_lambda_event_data_equal(d: Any):
    return lambda e, h: e.data == d


def tc_pattern(
        name: str = "pattern",
        data_blocks: Optional[List[Any]] = None,
        data_pres: Optional[List[Any]] = None,
        data_halts: Optional[List[Any]] = None) -> BoboPattern:
    if data_blocks is None:
        data_blocks = [1]

    if data_pres is None:
        data_pres = []

    if data_halts is None:
        data_halts = []

    blocks: List[BoboPatternBlock] = []
    for i in range(len(data_blocks)):
        blocks.append(tc_block(
            group="g{}".format(i + 1),
            call=tc_lambda_event_data_equal(data_blocks[i])))

    preconditions: List[BoboPredicate] = []
    for i in range(len(data_pres)):
        preconditions.append(BoboPredicateCall(
            call=tc_lambda_event_data_equal(data_pres[i])))

    haltconditions: List[BoboPredicate] = []
    for i in range(len(data_halts)):
        haltconditions.append(BoboPredicateCall(
            call=tc_lambda_event_data_equal(data_halts[i])))

    return BoboPattern(
        name=name,
        blocks=blocks,
        preconditions=preconditions,
        haltconditions=haltconditions)
