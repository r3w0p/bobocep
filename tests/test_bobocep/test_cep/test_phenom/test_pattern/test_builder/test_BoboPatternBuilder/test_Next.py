# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from bobocep.cep.phenom.pattern.builder import BoboPatternBuilder
from bobocep.cep.phenom.pattern.predicate import BoboPredicateCall


class TestValid:

    def test_1_block_1_precon_1_haltcon(self):
        name = "name"
        group_a = "group_a"
        predicate_block_a = BoboPredicateCall(call=lambda e, h: True)
        predicate_pre_a = BoboPredicateCall(call=lambda e, h: True)
        predicate_halt_a = BoboPredicateCall(call=lambda e, h: True)

        builder = BoboPatternBuilder(name=name) \
            .next(predicate=predicate_block_a,
                  group=group_a,
                  times=1,
                  loop=False) \
            .precondition(predicate=predicate_pre_a) \
            .haltcondition(predicate=predicate_halt_a)

        pattern = builder.generate()

        assert pattern.name == name
        assert len(pattern.blocks) == 1
        assert len(pattern.preconditions) == 1
        assert len(pattern.haltconditions) == 1

        assert len(pattern.blocks[0].predicates) == 1

        assert pattern.blocks[0].group == group_a
        assert pattern.blocks[0].predicates[0] == predicate_block_a
        assert pattern.blocks[0].strict is True
        assert pattern.blocks[0].loop is False
        assert pattern.blocks[0].negated is False
        assert pattern.blocks[0].optional is False

        assert pattern.preconditions[0] == predicate_pre_a
        assert pattern.haltconditions[0] == predicate_halt_a

    def test_1_block_3_times(self):
        predicate_block_a = BoboPredicateCall(call=lambda e, h: True)

        builder = BoboPatternBuilder(name="pattern") \
            .next(group="group_a",
                  predicate=predicate_block_a,
                  times=3,
                  loop=False)

        pattern = builder.generate()

        assert len(pattern.blocks) == 3
        assert len(pattern.preconditions) == 0
        assert len(pattern.haltconditions) == 0

        assert len(pattern.blocks[0].predicates) == 1
        assert len(pattern.blocks[1].predicates) == 1
        assert len(pattern.blocks[2].predicates) == 1

        assert pattern.blocks[0].predicates[0] == predicate_block_a
        assert pattern.blocks[1].predicates[0] == predicate_block_a
        assert pattern.blocks[2].predicates[0] == predicate_block_a

    def test_3_block_3_precon_3_haltcon(self):
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
                  predicate=predicate_block_a,
                  times=1,
                  loop=False) \
            .next(group="group_b",
                  predicate=predicate_block_b,
                  times=1,
                  loop=False) \
            .next(group="group_c",
                  predicate=predicate_block_c,
                  times=1,
                  loop=False) \
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
