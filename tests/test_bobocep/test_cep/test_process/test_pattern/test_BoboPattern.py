# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

import tests.common as tc
from bobocep.cep.process import BoboPattern
from bobocep.cep.process.pattern import BoboPatternError


class TestInvalid:

    def test_name_0_length(self):
        with pytest.raises(BoboPatternError):
            BoboPattern(name="",
                        blocks=[tc.block("a")],
                        preconditions=[tc.predicate()],
                        haltconditions=[tc.predicate()])

    def test_blocks_0_length(self):
        with pytest.raises(BoboPatternError):
            BoboPattern(name="pattern",
                        blocks=[],
                        preconditions=[tc.predicate()],
                        haltconditions=[tc.predicate()])

    def test_3_blocks_first_block_negated(self):
        with pytest.raises(BoboPatternError):
            BoboPattern(name="pattern",
                        blocks=[tc.block("a", negated=True),
                                tc.block("b"),
                                tc.block("c")],
                        preconditions=[tc.predicate()],
                        haltconditions=[tc.predicate()])

    def test_3_blocks_first_block_optional(self):
        with pytest.raises(BoboPatternError):
            BoboPattern(name="pattern",
                        blocks=[tc.block("a", optional=True),
                                tc.block("b"),
                                tc.block("c")],
                        preconditions=[tc.predicate()],
                        haltconditions=[tc.predicate()])

    def test_3_blocks_first_block_loop(self):
        with pytest.raises(BoboPatternError):
            BoboPattern(name="pattern",
                        blocks=[tc.block("a", loop=True),
                                tc.block("b"),
                                tc.block("c")],
                        preconditions=[tc.predicate()],
                        haltconditions=[tc.predicate()])

    def test_3_blocks_last_block_negated(self):
        with pytest.raises(BoboPatternError):
            BoboPattern(name="pattern",
                        blocks=[tc.block("a"),
                                tc.block("b"),
                                tc.block("c", negated=True)],
                        preconditions=[tc.predicate()],
                        haltconditions=[tc.predicate()])

    def test_3_blocks_last_block_optional(self):
        with pytest.raises(BoboPatternError):
            BoboPattern(name="pattern",
                        blocks=[tc.block("a"),
                                tc.block("b"),
                                tc.block("c", optional=True)],
                        preconditions=[tc.predicate()],
                        haltconditions=[tc.predicate()])

    def test_3_blocks_last_block_loop(self):
        with pytest.raises(BoboPatternError):
            BoboPattern(name="pattern",
                        blocks=[tc.block("a"),
                                tc.block("b"),
                                tc.block("c", loop=True)],
                        preconditions=[tc.predicate()],
                        haltconditions=[tc.predicate()])
