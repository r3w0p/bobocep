# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
import pytest

from bobocep.cep.phenomenon.pattern.builder import BoboPatternBuilder
from bobocep.cep.phenomenon.pattern.pattern import BoboPatternError
from bobocep.cep.phenomenon.pattern.predicate import BoboPredicateCall


class TestValid:

    def test_3_block_1_not_next_3_precon_3_haltcon(self):
        predicate_block_a = BoboPredicateCall(call=lambda e, h: True)
        predicate_block_b = lambda e, h: True
        predicate_block_c = BoboPredicateCall(call=lambda e, h: True)

        predicate_pre_a = BoboPredicateCall(call=lambda e, h: True)
        predicate_pre_b = lambda e, h: True
        predicate_pre_c = BoboPredicateCall(call=lambda e, h: True)

        predicate_halt_a = BoboPredicateCall(call=lambda e, h: True)
        predicate_halt_b = lambda e, h: True
        predicate_halt_c = BoboPredicateCall(call=lambda e, h: True)

        builder = BoboPatternBuilder(name="pattern") \
            .next(group="group_a",
                  predicate=predicate_block_a) \
            .not_next(group="group_b",
                      predicate=predicate_block_b) \
            .next(group="group_c",
                  predicate=predicate_block_c) \
            .precondition(predicate=predicate_pre_a) \
            .precondition(predicate=predicate_pre_b) \
            .precondition(predicate=predicate_pre_c) \
            .haltcondition(predicate=predicate_halt_a) \
            .haltcondition(predicate=predicate_halt_b) \
            .haltcondition(predicate=predicate_halt_c)

        pattern = builder.generate()

        assert len(pattern.blocks) == 3
        assert len(pattern.preconditions) == 3
        assert len(pattern.haltconditions) == 3

        assert len(pattern.blocks[0].predicates) == 1
        assert len(pattern.blocks[1].predicates) == 1
        assert len(pattern.blocks[2].predicates) == 1


class TestInvalid:

    def test_1_block_1_precon_1_haltcon_error(self):
        predicate_block_a = BoboPredicateCall(call=lambda e, h: True)
        predicate_pre_a = BoboPredicateCall(call=lambda e, h: True)
        predicate_halt_a = BoboPredicateCall(call=lambda e, h: True)

        builder = BoboPatternBuilder(name="pattern") \
            .not_next(group="group_a",
                      predicate=predicate_block_a) \
            .precondition(predicate=predicate_pre_a) \
            .haltcondition(predicate=predicate_halt_a)

        with pytest.raises(BoboPatternError):
            builder.generate()
