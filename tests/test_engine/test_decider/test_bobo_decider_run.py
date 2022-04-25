# Copyright (c) 2022 The BoboCEP Authors
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

import pytest
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


def test_pattern_3_block_halt_complete_process_to_complete():
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


def test_pattern_4_block_not_match_optional_process_to_complete():
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
