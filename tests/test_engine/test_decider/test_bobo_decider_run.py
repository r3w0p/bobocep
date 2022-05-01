# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from datetime import datetime

from bobocep.engine.decider.bobo_decider_run import BoboDeciderRun
from bobocep.events.bobo_event_primitive import BoboEventPrimitive
from bobocep.pattern.bobo_pattern_builder import BoboPatternBuilder
from bobocep.predicate.bobo_predicate_callable import BoboPredicateCallable


def test_pattern_1_block_halt_complete_on_init():
    pattern = BoboPatternBuilder() \
        .followed_by("group_a", BoboPredicateCallable(lambda e, h: True)) \
        .generate("pattern")

    event = BoboEventPrimitive("event_id", datetime.now(), None)
    run = BoboDeciderRun("run_id", pattern, event)

    assert run.is_halted()
    assert run.is_complete()


def test_pattern_3_block_halt_complete_on_init():
    pattern = BoboPatternBuilder() \
        .followed_by("group_a", BoboPredicateCallable(lambda e, h: True)) \
        .followed_by("group_b", BoboPredicateCallable(lambda e, h: True)) \
        .followed_by("group_c", BoboPredicateCallable(lambda e, h: True)) \
        .generate("pattern")

    event = BoboEventPrimitive("event_id", datetime.now(), None)
    run = BoboDeciderRun("run_id", pattern, event)

    assert not run.is_halted()
    assert not run.is_complete()


def test_pattern_3_block_halt_complete_to_complete():
    pattern = BoboPatternBuilder() \
        .followed_by("group_a", BoboPredicateCallable(lambda e, h: True)) \
        .followed_by("group_b", BoboPredicateCallable(lambda e, h: True)) \
        .followed_by("group_c", BoboPredicateCallable(lambda e, h: True)) \
        .generate("pattern")

    run = BoboDeciderRun("run_id", pattern,
                         BoboEventPrimitive("event_a", datetime.now(), None))

    run.process(BoboEventPrimitive("event_b", datetime.now(), None))
    assert not run.is_halted()
    assert not run.is_complete()

    run.process(BoboEventPrimitive("event_c", datetime.now(), None))
    assert run.is_halted()
    assert run.is_complete()


def test_pattern_3_block_manual_halt_not_complete():
    pattern = BoboPatternBuilder() \
        .followed_by("group_a", BoboPredicateCallable(lambda e, h: True)) \
        .followed_by("group_b", BoboPredicateCallable(lambda e, h: True)) \
        .followed_by("group_c", BoboPredicateCallable(lambda e, h: True)) \
        .generate("pattern")

    run = BoboDeciderRun("run_id", pattern,
                         BoboEventPrimitive("event_a", datetime.now(), None))

    run.halt()
    assert run.is_halted()
    assert not run.is_complete()


def test_pattern_3_block_process_on_halt():
    pattern = BoboPatternBuilder() \
        .followed_by("group_a", BoboPredicateCallable(lambda e, h: True)) \
        .followed_by("group_b", BoboPredicateCallable(lambda e, h: True)) \
        .followed_by("group_c", BoboPredicateCallable(lambda e, h: True)) \
        .generate("pattern")

    run = BoboDeciderRun("run_id", pattern,
                         BoboEventPrimitive("event_a", datetime.now(), None))

    run.halt()
    run.process(BoboEventPrimitive("event_b", datetime.now(), None))
    assert run.is_halted()


def test_pattern_3_block_halt_no_match_on_strict():
    pattern = BoboPatternBuilder() \
        .followed_by("group_a", BoboPredicateCallable(lambda e, h: True)) \
        .next("group_b", BoboPredicateCallable(lambda e, h: False)) \
        .followed_by("group_c", BoboPredicateCallable(lambda e, h: True)) \
        .generate("pattern")

    run = BoboDeciderRun("run_id", pattern,
                         BoboEventPrimitive("event_a", datetime.now(), None))

    run.process(BoboEventPrimitive("event_b", datetime.now(), None))
    assert run.is_halted()
    assert not run.is_complete()


def test_pattern_3_block_halt_no_match_on_strict_negated_to_complete():
    pattern = BoboPatternBuilder() \
        .followed_by("group_a", BoboPredicateCallable(lambda e, h: True)) \
        .not_next("group_b", BoboPredicateCallable(lambda e, h: False)) \
        .followed_by("group_c", BoboPredicateCallable(lambda e, h: True)) \
        .generate("pattern")

    run = BoboDeciderRun("run_id", pattern,
                         BoboEventPrimitive("event_a", datetime.now(), None))

    run.process(BoboEventPrimitive("event_b", datetime.now(), None))
    assert not run.is_halted()
    assert not run.is_complete()

    run.process(BoboEventPrimitive("event_c", datetime.now(), None))
    assert run.is_halted()
    assert run.is_complete()


def test_pattern_3_block_halt_match_on_strict_negated():
    pattern = BoboPatternBuilder() \
        .followed_by("group_a", BoboPredicateCallable(lambda e, h: True)) \
        .not_next("group_b", BoboPredicateCallable(lambda e, h: True)) \
        .followed_by("group_c", BoboPredicateCallable(lambda e, h: True)) \
        .generate("pattern")

    run = BoboDeciderRun("run_id", pattern,
                         BoboEventPrimitive("event_a", datetime.now(), None))

    run.process(BoboEventPrimitive("event_b", datetime.now(), None))
    assert run.is_halted()
    assert not run.is_complete()


def test_pattern_4_block_not_match_optional_to_complete():
    pattern = BoboPatternBuilder() \
        .followed_by("group_a", BoboPredicateCallable(lambda e, h: True)) \
        .followed_by("group_b", BoboPredicateCallable(lambda e, h: False),
                     optional=True) \
        .followed_by("group_c", BoboPredicateCallable(lambda e, h: True)) \
        .followed_by("group_d", BoboPredicateCallable(lambda e, h: True)) \
        .generate("pattern")

    run = BoboDeciderRun("run_id", pattern,
                         BoboEventPrimitive("event_a", datetime.now(), None))

    run.process(BoboEventPrimitive("event_b", datetime.now(), None))
    assert not run.is_halted()
    assert not run.is_complete()

    run.process(BoboEventPrimitive("event_c", datetime.now(), None))
    assert run.is_halted()
    assert run.is_complete()


def test_pattern_4_block_match_optional_to_complete():
    pattern = BoboPatternBuilder() \
        .followed_by("group_a", BoboPredicateCallable(lambda e, h: True)) \
        .followed_by("group_b", BoboPredicateCallable(lambda e, h: True),
                     optional=True) \
        .followed_by("group_c", BoboPredicateCallable(lambda e, h: True)) \
        .followed_by("group_d", BoboPredicateCallable(lambda e, h: True)) \
        .generate("pattern")

    run = BoboDeciderRun("run_id", pattern,
                         BoboEventPrimitive("event_a", datetime.now(), None))

    run.process(BoboEventPrimitive("event_b", datetime.now(), None))
    assert not run.is_halted()
    assert not run.is_complete()

    run.process(BoboEventPrimitive("event_c", datetime.now(), None))
    assert not run.is_halted()
    assert not run.is_complete()

    run.process(BoboEventPrimitive("event_d", datetime.now(), None))
    assert run.is_halted()
    assert run.is_complete()


def test_pattern_4_block_not_match_optional_then_loop():
    pattern = BoboPatternBuilder() \
        .followed_by("group_a", BoboPredicateCallable(lambda e, h: True)) \
        .followed_by("group_b", BoboPredicateCallable(lambda e, h: True),
                     optional=False) \
        .followed_by("group_c", BoboPredicateCallable(lambda e, h: True),
                     loop=True) \
        .followed_by("group_d", BoboPredicateCallable(lambda e, h: True)) \
        .generate("pattern")

    run = BoboDeciderRun("run_id", pattern,
                         BoboEventPrimitive("event_a", datetime.now(), None))

    run.process(BoboEventPrimitive("event_b", datetime.now(), None))
    assert not run.is_halted()
    assert not run.is_complete()

    run.process(BoboEventPrimitive("event_c", datetime.now(), None))
    assert not run.is_halted()
    assert not run.is_complete()

    run.process(BoboEventPrimitive("event_d", datetime.now(), None))
    assert not run.is_halted()
    assert not run.is_complete()

    run.process(BoboEventPrimitive("event_e", datetime.now(), None))
    assert not run.is_halted()
    assert not run.is_complete()


def test_pattern_4_block_match_optional_then_loop():
    pattern = BoboPatternBuilder() \
        .followed_by("group_a", BoboPredicateCallable(lambda e, h: True)) \
        .followed_by("group_b", BoboPredicateCallable(lambda e, h: True),
                     optional=True) \
        .followed_by("group_c", BoboPredicateCallable(lambda e, h: True),
                     loop=True) \
        .followed_by("group_d", BoboPredicateCallable(lambda e, h: True)) \
        .generate("pattern")

    run = BoboDeciderRun("run_id", pattern,
                         BoboEventPrimitive("event_a", datetime.now(), None))

    run.process(BoboEventPrimitive("event_b", datetime.now(), None))
    assert not run.is_halted()
    assert not run.is_complete()

    run.process(BoboEventPrimitive("event_c", datetime.now(), None))
    assert not run.is_halted()
    assert not run.is_complete()

    run.process(BoboEventPrimitive("event_d", datetime.now(), None))
    assert not run.is_halted()
    assert not run.is_complete()

    run.process(BoboEventPrimitive("event_e", datetime.now(), None))
    assert not run.is_halted()
    assert not run.is_complete()


def test_pattern_3_block_loop_not_match_strict():
    pattern = BoboPatternBuilder() \
        .followed_by("group_a", BoboPredicateCallable(lambda e, h: e.data)) \
        .next("group_b", BoboPredicateCallable(lambda e, h: e.data),
              loop=True) \
        .followed_by("group_c", BoboPredicateCallable(lambda e, h: e.data)) \
        .generate("pattern")

    run = BoboDeciderRun("run_id", pattern,
                         BoboEventPrimitive("event_a", datetime.now(), True))

    run.process(BoboEventPrimitive("event_b", datetime.now(), True))
    assert not run.is_halted()
    assert not run.is_complete()

    run.process(BoboEventPrimitive("event_c", datetime.now(), True))
    assert not run.is_halted()
    assert not run.is_complete()

    run.process(BoboEventPrimitive("event_d", datetime.now(), False))
    assert run.is_halted()
    assert not run.is_complete()


def test_pattern_3_block_loop_to_complete():
    pattern = BoboPatternBuilder() \
        .followed_by("group_a",
                     BoboPredicateCallable(lambda e, h: e.data == 1)) \
        .followed_by("group_b",
                     BoboPredicateCallable(lambda e, h: e.data == 2),
                     loop=True) \
        .followed_by("group_c",
                     BoboPredicateCallable(lambda e, h: e.data == 3)) \
        .generate("pattern")

    run = BoboDeciderRun("run_id", pattern,
                         BoboEventPrimitive("event_a", datetime.now(), 1))

    run.process(BoboEventPrimitive("event_b", datetime.now(), 2))
    assert not run.is_halted()
    assert not run.is_complete()

    run.process(BoboEventPrimitive("event_c", datetime.now(), 2))
    assert not run.is_halted()
    assert not run.is_complete()

    run.process(BoboEventPrimitive("event_d", datetime.now(), 3))
    assert run.is_halted()
    assert run.is_complete()


def test_pattern_4_block_2_loop_to_complete():
    pattern = BoboPatternBuilder() \
        .followed_by("group_a",
                     BoboPredicateCallable(lambda e, h: e.data == 1)) \
        .followed_by("group_b",
                     BoboPredicateCallable(lambda e, h: e.data == 2),
                     loop=True) \
        .followed_by("group_c",
                     BoboPredicateCallable(lambda e, h: e.data == 3),
                     loop=True) \
        .followed_by("group_d",
                     BoboPredicateCallable(lambda e, h: e.data == 4)) \
        .generate("pattern")

    run = BoboDeciderRun("run_id", pattern,
                         BoboEventPrimitive("event_a", datetime.now(), 1))

    run.process(BoboEventPrimitive("event_b", datetime.now(), 2))
    assert not run.is_halted()
    assert not run.is_complete()

    run.process(BoboEventPrimitive("event_c", datetime.now(), 2))
    assert not run.is_halted()
    assert not run.is_complete()

    run.process(BoboEventPrimitive("event_d", datetime.now(), 3))
    assert not run.is_halted()
    assert not run.is_complete()

    run.process(BoboEventPrimitive("event_e", datetime.now(), 3))
    assert not run.is_halted()
    assert not run.is_complete()

    run.process(BoboEventPrimitive("event_f", datetime.now(), 4))
    assert run.is_halted()
    assert run.is_complete()
