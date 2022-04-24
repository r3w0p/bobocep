# Copyright (c) The BoboCEP Authors
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from bobocep.pattern.bobo_pattern_builder import BoboPatternBuilder
from bobocep.predicate.bobo_predicate_callable import BoboPredicateCallable


def test_1_block_1_pre_1_halt():
    name_a = "name_a"
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

    pattern = builder.generate(name=name_a)

    assert pattern.name == name_a
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


def test_3_blocks_3_pres_3_halts():
    name_a = "name_a"
    group_a = "group_a"
    group_b = "group_b"
    group_c = "group_c"

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
        .next(group=group_a,
              predicate=predicate_block_a,
              times=1,
              loop=False) \
        .next(group=group_b,
              predicate=predicate_block_b,
              times=1,
              loop=False) \
        .next(group=group_c,
              predicate=predicate_block_c,
              times=1,
              loop=False) \
        .precondition(predicate=predicate_pre_a) \
        .precondition(predicate=predicate_pre_b) \
        .precondition(predicate=predicate_pre_c) \
        .haltcondition(predicate=predicate_halt_a) \
        .haltcondition(predicate=predicate_halt_b) \
        .haltcondition(predicate=predicate_halt_c)

    pattern = builder.generate(name=name_a)

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
