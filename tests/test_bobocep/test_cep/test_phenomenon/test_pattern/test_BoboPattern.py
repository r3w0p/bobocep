# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

from bobocep.cep.phenom.pattern.pattern import BoboPatternError, BoboPattern
from tests.test_bobocep.test_cep.test_phenomenon.test_pattern import tc_block
from tests.test_bobocep.test_cep.test_phenomenon.test_pattern.test_predicate import \
    tc_predicate


class TestInvalid:

    def test_name_0_length(self):
        with pytest.raises(BoboPatternError):
            BoboPattern(name="",
                        blocks=[tc_block(group="a")],
                        preconditions=[tc_predicate()],
                        haltconditions=[tc_predicate()])

    def test_blocks_0_length(self):
        with pytest.raises(BoboPatternError):
            BoboPattern(name="pattern",
                        blocks=[],
                        preconditions=[tc_predicate()],
                        haltconditions=[tc_predicate()])

    def test_3_blocks_first_block_negated(self):
        with pytest.raises(BoboPatternError):
            BoboPattern(name="pattern",
                        blocks=[tc_block(group="a", negated=True),
                                tc_block(group="b"),
                                tc_block(group="c")],
                        preconditions=[tc_predicate()],
                        haltconditions=[tc_predicate()])

    def test_3_blocks_first_block_optional(self):
        with pytest.raises(BoboPatternError):
            BoboPattern(name="pattern",
                        blocks=[tc_block(group="a", optional=True),
                                tc_block(group="b"),
                                tc_block(group="c")],
                        preconditions=[tc_predicate()],
                        haltconditions=[tc_predicate()])

    def test_3_blocks_first_block_loop(self):
        with pytest.raises(BoboPatternError):
            BoboPattern(name="pattern",
                        blocks=[tc_block(group="a", loop=True),
                                tc_block(group="b"),
                                tc_block(group="c")],
                        preconditions=[tc_predicate()],
                        haltconditions=[tc_predicate()])

    def test_3_blocks_last_block_negated(self):
        with pytest.raises(BoboPatternError):
            BoboPattern(name="pattern",
                        blocks=[tc_block(group="a"),
                                tc_block(group="b"),
                                tc_block(group="c", negated=True)],
                        preconditions=[tc_predicate()],
                        haltconditions=[tc_predicate()])

    def test_3_blocks_last_block_optional(self):
        with pytest.raises(BoboPatternError):
            BoboPattern(name="pattern",
                        blocks=[tc_block(group="a"),
                                tc_block(group="b"),
                                tc_block(group="c", optional=True)],
                        preconditions=[tc_predicate()],
                        haltconditions=[tc_predicate()])

    def test_3_blocks_last_block_loop(self):
        with pytest.raises(BoboPatternError):
            BoboPattern(name="pattern",
                        blocks=[tc_block(group="a"),
                                tc_block(group="b"),
                                tc_block(group="c", loop=True)],
                        preconditions=[tc_predicate()],
                        haltconditions=[tc_predicate()])
