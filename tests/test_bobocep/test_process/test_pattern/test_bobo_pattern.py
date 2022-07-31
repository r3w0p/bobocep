# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from typing import Callable

import pytest

from bobocep.process.pattern.bobo_pattern import BoboPattern
from bobocep.process.pattern.bobo_pattern_block import BoboPatternBlock
from bobocep.process.pattern.bobo_pattern_error import BoboPatternError
from bobocep.process.pattern.predicate.bobo_predicate_call import \
    BoboPredicateCall


def _block(group: str,
           call: Callable = lambda e, h: e.data,
           strict: bool = False,
           loop: bool = False,
           negated: bool = False,
           optional: bool = False):
    return BoboPatternBlock(
        group=group,
        predicates=[BoboPredicateCall(call=call)],
        strict=strict,
        loop=loop,
        negated=negated,
        optional=optional)


def _predicate(call: Callable = lambda e, h: True):
    return BoboPredicateCall(call=call)


class TestInvalid:

    def test_name_0_length(self):
        with pytest.raises(BoboPatternError):
            BoboPattern(name="",
                        blocks=[_block("a")],
                        preconditions=[_predicate()],
                        haltconditions=[_predicate()])

    def test_blocks_0_length(self):
        with pytest.raises(BoboPatternError):
            BoboPattern(name="pattern",
                        blocks=[],
                        preconditions=[_predicate()],
                        haltconditions=[_predicate()])

    def test_3_blocks_first_block_negated(self):
        block_first = _block("a", negated=True)
        block_mid = _block("b")
        block_last = _block("c")

        with pytest.raises(BoboPatternError):
            BoboPattern(name="pattern",
                        blocks=[block_first, block_mid, block_last],
                        preconditions=[_predicate()],
                        haltconditions=[_predicate()])

    def test_3_blocks_first_block_optional(self):
        block_first = _block("a", optional=True)
        block_mid = _block("b")
        block_last = _block("c")

        with pytest.raises(BoboPatternError):
            BoboPattern(name="pattern",
                        blocks=[block_first, block_mid, block_last],
                        preconditions=[_predicate()],
                        haltconditions=[_predicate()])

    def test_3_blocks_first_block_loop(self):
        block_first = _block("a", loop=True)
        block_mid = _block("b")
        block_last = _block("c")

        with pytest.raises(BoboPatternError):
            BoboPattern(name="pattern",
                        blocks=[block_first, block_mid, block_last],
                        preconditions=[_predicate()],
                        haltconditions=[_predicate()])

    def test_3_blocks_last_block_negated(self):
        block_first = _block("a")
        block_mid = _block("b")
        block_last = _block("c", negated=True)

        with pytest.raises(BoboPatternError):
            BoboPattern(name="pattern",
                        blocks=[block_first, block_mid, block_last],
                        preconditions=[_predicate()],
                        haltconditions=[_predicate()])

    def test_3_blocks_last_block_optional(self):
        block_first = _block("a")
        block_mid = _block("b")
        block_last = _block("c", optional=True)

        with pytest.raises(BoboPatternError):
            BoboPattern(name="pattern",
                        blocks=[block_first, block_mid, block_last],
                        preconditions=[_predicate()],
                        haltconditions=[_predicate()])

    def test_3_blocks_last_block_loop(self):
        block_first = _block("a")
        block_mid = _block("b")
        block_last = _block("c", loop=True)

        with pytest.raises(BoboPatternError):
            BoboPattern(name="pattern",
                        blocks=[block_first, block_mid, block_last],
                        preconditions=[_predicate()],
                        haltconditions=[_predicate()])
