# Copyright (c) 2022 The BoboCEP Authors
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from bobocep.pattern.bobo_pattern_builder import BoboPatternBuilder
from bobocep.predicate.bobo_predicate_callable import BoboPredicateCallable


class TestNext:

    def test_1_block_1_precon_1_haltcon(self):
        name = "name"
        group_a = "group_a"
        predicate_block_a = BoboPredicateCallable(call=lambda e, h: True)
        predicate_pre_a = BoboPredicateCallable(call=lambda e, h: True)
        predicate_halt_a = BoboPredicateCallable(call=lambda e, h: True)

        builder = BoboPatternBuilder() \
            .next(group=group_a,
                  predicate=predicate_block_a,
                  times=1,
                  loop=False) \
            .precondition(predicate=predicate_pre_a) \
            .haltcondition(predicate=predicate_halt_a)

        pattern = builder.generate(name=name)

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
        predicate_block_a = BoboPredicateCallable(call=lambda e, h: True)

        builder = BoboPatternBuilder() \
            .next(group="group_a",
                  predicate=predicate_block_a,
                  times=3,
                  loop=False)

        pattern = builder.generate(name="name")

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
        predicate_block_a = BoboPredicateCallable(call=lambda e, h: True)
        predicate_block_b = BoboPredicateCallable(call=lambda e, h: True)
        predicate_block_c = BoboPredicateCallable(call=lambda e, h: True)

        predicate_pre_a = BoboPredicateCallable(call=lambda e, h: True)
        predicate_pre_b = BoboPredicateCallable(call=lambda e, h: True)
        predicate_pre_c = BoboPredicateCallable(call=lambda e, h: True)

        predicate_halt_a = BoboPredicateCallable(call=lambda e, h: True)
        predicate_halt_b = BoboPredicateCallable(call=lambda e, h: True)
        predicate_halt_c = BoboPredicateCallable(call=lambda e, h: True)

        builder = BoboPatternBuilder() \
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

        pattern = builder.generate(name="name")

        assert len(pattern.blocks) == 3
        assert len(pattern.preconditions) == 3
        assert len(pattern.haltconditions) == 3

        assert len(pattern.blocks[0].predicates) == 1
        assert len(pattern.blocks[1].predicates) == 1
        assert len(pattern.blocks[2].predicates) == 1

        assert pattern.blocks[0].predicates[0] == predicate_block_a
        assert pattern.blocks[1].predicates[0] == predicate_block_b
        assert pattern.blocks[2].predicates[0] == predicate_block_c

        assert pattern.preconditions[0] == predicate_pre_a
        assert pattern.preconditions[1] == predicate_pre_b
        assert pattern.preconditions[2] == predicate_pre_c

        assert pattern.haltconditions[0] == predicate_halt_a
        assert pattern.haltconditions[1] == predicate_halt_b
        assert pattern.haltconditions[2] == predicate_halt_c


class TestFollowedBy:

    def test_1_block_1_precon_1_haltcon(self):
        name = "name"
        group_a = "group_a"
        predicate_block_a = BoboPredicateCallable(call=lambda e, h: True)
        predicate_pre_a = BoboPredicateCallable(call=lambda e, h: True)
        predicate_halt_a = BoboPredicateCallable(call=lambda e, h: True)

        builder = BoboPatternBuilder() \
            .followed_by(group=group_a,
                         predicate=predicate_block_a,
                         times=1,
                         loop=False,
                         optional=False) \
            .precondition(predicate=predicate_pre_a) \
            .haltcondition(predicate=predicate_halt_a)

        pattern = builder.generate(name=name)

        assert pattern.name == name
        assert len(pattern.blocks) == 1
        assert len(pattern.preconditions) == 1
        assert len(pattern.haltconditions) == 1

        assert len(pattern.blocks[0].predicates) == 1

        assert pattern.blocks[0].group == group_a
        assert pattern.blocks[0].predicates[0] == predicate_block_a
        assert pattern.blocks[0].strict is False
        assert pattern.blocks[0].loop is False
        assert pattern.blocks[0].negated is False
        assert pattern.blocks[0].optional is False

        assert pattern.preconditions[0] == predicate_pre_a
        assert pattern.haltconditions[0] == predicate_halt_a

    def test_1_block_3_times(self):
        predicate_block_a = BoboPredicateCallable(call=lambda e, h: True)

        builder = BoboPatternBuilder() \
            .followed_by(group="group_a",
                         predicate=predicate_block_a,
                         times=3,
                         loop=False,
                         optional=False)

        pattern = builder.generate(name="name")

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
        predicate_block_a = BoboPredicateCallable(call=lambda e, h: True)
        predicate_block_b = BoboPredicateCallable(call=lambda e, h: True)
        predicate_block_c = BoboPredicateCallable(call=lambda e, h: True)

        predicate_pre_a = BoboPredicateCallable(call=lambda e, h: True)
        predicate_pre_b = BoboPredicateCallable(call=lambda e, h: True)
        predicate_pre_c = BoboPredicateCallable(call=lambda e, h: True)

        predicate_halt_a = BoboPredicateCallable(call=lambda e, h: True)
        predicate_halt_b = BoboPredicateCallable(call=lambda e, h: True)
        predicate_halt_c = BoboPredicateCallable(call=lambda e, h: True)

        builder = BoboPatternBuilder() \
            .followed_by(group="group_a",
                         predicate=predicate_block_a,
                         times=1,
                         loop=False,
                         optional=False) \
            .followed_by(group="group_b",
                         predicate=predicate_block_b,
                         times=1,
                         loop=False,
                         optional=False) \
            .followed_by(group="group_c",
                         predicate=predicate_block_c,
                         times=1,
                         loop=False,
                         optional=False) \
            .precondition(predicate=predicate_pre_a) \
            .precondition(predicate=predicate_pre_b) \
            .precondition(predicate=predicate_pre_c) \
            .haltcondition(predicate=predicate_halt_a) \
            .haltcondition(predicate=predicate_halt_b) \
            .haltcondition(predicate=predicate_halt_c)

        pattern = builder.generate(name="name")

        assert len(pattern.blocks) == 3
        assert len(pattern.preconditions) == 3
        assert len(pattern.haltconditions) == 3

        assert len(pattern.blocks[0].predicates) == 1
        assert len(pattern.blocks[1].predicates) == 1
        assert len(pattern.blocks[2].predicates) == 1

        assert pattern.blocks[0].predicates[0] == predicate_block_a
        assert pattern.blocks[1].predicates[0] == predicate_block_b
        assert pattern.blocks[2].predicates[0] == predicate_block_c

        assert pattern.preconditions[0] == predicate_pre_a
        assert pattern.preconditions[1] == predicate_pre_b
        assert pattern.preconditions[2] == predicate_pre_c

        assert pattern.haltconditions[0] == predicate_halt_a
        assert pattern.haltconditions[1] == predicate_halt_b
        assert pattern.haltconditions[2] == predicate_halt_c


class TestFollowedByAny:

    def test_1_block_3_pred_1_precon_1_haltcon(self):
        name = "name"
        group_a = "group_a"
        predicate_block_a_1 = BoboPredicateCallable(call=lambda e, h: True)
        predicate_block_a_2 = BoboPredicateCallable(call=lambda e, h: True)
        predicate_block_a_3 = BoboPredicateCallable(call=lambda e, h: True)
        predicate_pre_a = BoboPredicateCallable(call=lambda e, h: True)
        predicate_halt_a = BoboPredicateCallable(call=lambda e, h: True)

        builder = BoboPatternBuilder() \
            .followed_by_any(group=group_a,
                             predicates=[predicate_block_a_1,
                                         predicate_block_a_2,
                                         predicate_block_a_3],
                             times=1,
                             loop=False,
                             optional=False) \
            .precondition(predicate=predicate_pre_a) \
            .haltcondition(predicate=predicate_halt_a)

        pattern = builder.generate(name=name)

        assert pattern.name == name
        assert len(pattern.blocks) == 1
        assert len(pattern.preconditions) == 1
        assert len(pattern.haltconditions) == 1

        assert len(pattern.blocks[0].predicates) == 3

        assert pattern.blocks[0].group == group_a
        assert pattern.blocks[0].predicates[0] == predicate_block_a_1
        assert pattern.blocks[0].predicates[1] == predicate_block_a_2
        assert pattern.blocks[0].predicates[2] == predicate_block_a_3
        assert pattern.blocks[0].strict is False
        assert pattern.blocks[0].loop is False
        assert pattern.blocks[0].negated is False
        assert pattern.blocks[0].optional is False

        assert pattern.preconditions[0] == predicate_pre_a
        assert pattern.haltconditions[0] == predicate_halt_a

    def test_1_block_3_pred_3_times(self):
        predicate_block_a_1 = BoboPredicateCallable(call=lambda e, h: True)
        predicate_block_a_2 = BoboPredicateCallable(call=lambda e, h: True)
        predicate_block_a_3 = BoboPredicateCallable(call=lambda e, h: True)

        builder = BoboPatternBuilder() \
            .followed_by_any(group="group_a",
                             predicates=[predicate_block_a_1,
                                         predicate_block_a_2,
                                         predicate_block_a_3],
                             times=3,
                             loop=False,
                             optional=False)

        pattern = builder.generate(name="name")

        assert len(pattern.blocks) == 3
        assert len(pattern.preconditions) == 0
        assert len(pattern.haltconditions) == 0

        assert len(pattern.blocks[0].predicates) == 3
        assert len(pattern.blocks[1].predicates) == 3
        assert len(pattern.blocks[2].predicates) == 3

        assert pattern.blocks[0].predicates[0] == predicate_block_a_1
        assert pattern.blocks[0].predicates[1] == predicate_block_a_2
        assert pattern.blocks[0].predicates[2] == predicate_block_a_3

        assert pattern.blocks[1].predicates[0] == predicate_block_a_1
        assert pattern.blocks[1].predicates[1] == predicate_block_a_2
        assert pattern.blocks[1].predicates[2] == predicate_block_a_3

        assert pattern.blocks[2].predicates[0] == predicate_block_a_1
        assert pattern.blocks[2].predicates[1] == predicate_block_a_2
        assert pattern.blocks[2].predicates[2] == predicate_block_a_3

    def test_3_block_3_pred_3_precon_3_haltcon(self):
        predicate_block_a_1 = BoboPredicateCallable(call=lambda e, h: True)
        predicate_block_a_2 = BoboPredicateCallable(call=lambda e, h: True)
        predicate_block_a_3 = BoboPredicateCallable(call=lambda e, h: True)

        predicate_block_b_1 = BoboPredicateCallable(call=lambda e, h: True)
        predicate_block_b_2 = BoboPredicateCallable(call=lambda e, h: True)
        predicate_block_b_3 = BoboPredicateCallable(call=lambda e, h: True)

        predicate_block_c_1 = BoboPredicateCallable(call=lambda e, h: True)
        predicate_block_c_2 = BoboPredicateCallable(call=lambda e, h: True)
        predicate_block_c_3 = BoboPredicateCallable(call=lambda e, h: True)

        predicate_pre_a = BoboPredicateCallable(call=lambda e, h: True)
        predicate_pre_b = BoboPredicateCallable(call=lambda e, h: True)
        predicate_pre_c = BoboPredicateCallable(call=lambda e, h: True)

        predicate_halt_a = BoboPredicateCallable(call=lambda e, h: True)
        predicate_halt_b = BoboPredicateCallable(call=lambda e, h: True)
        predicate_halt_c = BoboPredicateCallable(call=lambda e, h: True)

        builder = BoboPatternBuilder() \
            .followed_by_any(group="group_a",
                             predicates=[predicate_block_a_1,
                                         predicate_block_a_2,
                                         predicate_block_a_3],
                             times=1,
                             loop=False,
                             optional=False) \
            .followed_by_any(group="group_b",
                             predicates=[predicate_block_b_1,
                                         predicate_block_b_2,
                                         predicate_block_b_3],
                             times=1,
                             loop=False,
                             optional=False) \
            .followed_by_any(group="group_c",
                             predicates=[predicate_block_c_1,
                                         predicate_block_c_2,
                                         predicate_block_c_3],
                             times=1,
                             loop=False,
                             optional=False) \
            .precondition(predicate=predicate_pre_a) \
            .precondition(predicate=predicate_pre_b) \
            .precondition(predicate=predicate_pre_c) \
            .haltcondition(predicate=predicate_halt_a) \
            .haltcondition(predicate=predicate_halt_b) \
            .haltcondition(predicate=predicate_halt_c)

        pattern = builder.generate(name="name")

        assert len(pattern.blocks) == 3
        assert len(pattern.preconditions) == 3
        assert len(pattern.haltconditions) == 3

        assert pattern.blocks[0].predicates[0] == predicate_block_a_1
        assert pattern.blocks[0].predicates[1] == predicate_block_a_2
        assert pattern.blocks[0].predicates[2] == predicate_block_a_3

        assert pattern.blocks[1].predicates[0] == predicate_block_b_1
        assert pattern.blocks[1].predicates[1] == predicate_block_b_2
        assert pattern.blocks[1].predicates[2] == predicate_block_b_3

        assert pattern.blocks[2].predicates[0] == predicate_block_c_1
        assert pattern.blocks[2].predicates[1] == predicate_block_c_2
        assert pattern.blocks[2].predicates[2] == predicate_block_c_3

        assert pattern.preconditions[0] == predicate_pre_a
        assert pattern.preconditions[1] == predicate_pre_b
        assert pattern.preconditions[2] == predicate_pre_c

        assert pattern.haltconditions[0] == predicate_halt_a
        assert pattern.haltconditions[1] == predicate_halt_b
        assert pattern.haltconditions[2] == predicate_halt_c
