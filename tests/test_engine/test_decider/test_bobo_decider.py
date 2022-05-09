# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from datetime import datetime
from typing import List, Callable, Tuple

from bobocep.engine.decider.bobo_decider import BoboDecider
from bobocep.engine.decider.bobo_decider_run import BoboDeciderRun
from bobocep.engine.decider.bobo_decider_subscriber import \
    BoboDeciderSubscriber
from bobocep.event.bobo_event_simple import BoboEventSimple
from bobocep.event.event_id.bobo_event_id import BoboEventID
from bobocep.event.event_id.bobo_event_id_unique import BoboEventIDUnique
from bobocep.pattern.bobo_pattern import BoboPattern
from bobocep.pattern.bobo_pattern_block import BoboPatternBlock
from bobocep.predicate.bobo_predicate_call import BoboPredicateCall


def _simple(event_id: str = "event_id",
            timestamp: datetime = None,
            data=None):
    return BoboEventSimple(
        event_id=event_id,
        timestamp=timestamp if timestamp is not None else datetime.now(),
        data=data)


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


def _pattern_3_blocks_1_pre_1_halt(
        name: str,
        groups: Tuple[str, str, str],
        data_blocks: Tuple[int, int, int],
        data_pre: str,
        data_halt: str):
    block_1 = _block(groups[0], call=lambda e, h: e.data == data_blocks[0])
    block_2 = _block(groups[1], call=lambda e, h: e.data == data_blocks[1])
    block_3 = _block(groups[2], call=lambda e, h: e.data == data_blocks[2])
    pre_a = BoboPredicateCall(call=lambda e, h: e.data == data_pre)
    halt_b = BoboPredicateCall(call=lambda e, h: e.data == data_halt)

    return BoboPattern(
        name=name,
        blocks=[block_1, block_2, block_3],
        preconditions=[pre_a],
        haltconditions=[halt_b])


def _decsub(patterns: List[BoboPattern],
            event_id_gen: BoboEventID = None,
            run_id_gen: BoboEventID = None,
            max_size: int = 255):
    decider = BoboDecider(
        patterns=patterns,
        event_id_gen=event_id_gen if event_id_gen is not None else
        BoboEventIDUnique(),
        run_id_gen=run_id_gen if run_id_gen is not None else
        BoboEventIDUnique(),
        max_size=max_size)

    subscriber = StubDeciderSubscriber()
    decider.subscribe(subscriber=subscriber)

    return decider, subscriber


class StubDeciderSubscriber(BoboDeciderSubscriber):
    def __init__(self):
        super().__init__()
        self.runs = []

    def on_decider_completed_run(self, run: BoboDeciderRun):
        self.runs.append(run)


class TestValid:

    def test_3_patterns_init(self):
        pattern_123_ab = _pattern_3_blocks_1_pre_1_halt(
            "pattern_123_ab", ("1", "2", "3"), (1, 2, 3), "a", "b")

        pattern_456_cd = _pattern_3_blocks_1_pre_1_halt(
            "pattern_456_cd", ("1", "2", "3"), (4, 5, 6), "c", "d")

        pattern_789_ef = _pattern_3_blocks_1_pre_1_halt(
            "pattern_789_ef", ("1", "2", "3"), (7, 8, 9), "e", "f")

        decider = BoboDecider(
            patterns=[pattern_123_ab, pattern_456_cd, pattern_789_ef],
            event_id_gen=BoboEventIDUnique(),
            run_id_gen=BoboEventIDUnique(),
            max_size=255)

        decider_patterns = decider.patterns()

        assert len(decider_patterns) == 3
        assert pattern_123_ab in decider_patterns
        assert pattern_456_cd in decider_patterns
        assert pattern_789_ef in decider_patterns
        assert len(decider.all_runs()) == 0
        assert decider.size() == 0

    def test_3_distinct_patterns_1_run_per_pattern(self):
        pattern_123_ab = _pattern_3_blocks_1_pre_1_halt(
            "pattern_123_ab", ("1", "2", "3"), (1, 2, 3), "a", "b")

        pattern_456_cd = _pattern_3_blocks_1_pre_1_halt(
            "pattern_456_cd", ("1", "2", "3"), (4, 5, 6), "c", "d")

        pattern_789_ef = _pattern_3_blocks_1_pre_1_halt(
            "pattern_789_ef", ("1", "2", "3"), (7, 8, 9), "e", "f")

        decider = BoboDecider(
            patterns=[pattern_123_ab, pattern_456_cd, pattern_789_ef],
            event_id_gen=BoboEventIDUnique(),
            run_id_gen=BoboEventIDUnique(),
            max_size=255)

        for event, pattern in [
            (_simple(data=1), pattern_123_ab),
            (_simple(data=4), pattern_456_cd),
            (_simple(data=7), pattern_789_ef)
        ]:
            decider.on_receiver_event(event=event)
            assert decider.size() == 1

            decider.update()
            assert decider.size() == 0
            assert len(decider.runs_from(pattern=pattern.name)) == 1
            assert decider.runs_from(
                pattern=pattern.name)[0].pattern == pattern

    def test_3_patterns_same_blocks(self):
        pattern_123_ab_1 = _pattern_3_blocks_1_pre_1_halt(
            "pattern_123_ab_1", ("1", "2", "3"), (1, 2, 3), "a", "b")

        pattern_123_ab_2 = _pattern_3_blocks_1_pre_1_halt(
            "pattern_123_ab_2", ("1", "2", "3"), (1, 2, 3), "a", "b")

        pattern_123_ab_3 = _pattern_3_blocks_1_pre_1_halt(
            "pattern_123_ab_3", ("1", "2", "3"), (1, 2, 3), "a", "b")

        decider = BoboDecider(
            patterns=[pattern_123_ab_1, pattern_123_ab_2, pattern_123_ab_3],
            event_id_gen=BoboEventIDUnique(),
            run_id_gen=BoboEventIDUnique(),
            max_size=255)

        decider.on_receiver_event(event=_simple(data=1))
        decider.update()

        assert decider.size() == 0
        assert len(decider.runs_from(pattern=pattern_123_ab_1.name)) == 1
        assert len(decider.runs_from(pattern=pattern_123_ab_2.name)) == 1
        assert len(decider.runs_from(pattern=pattern_123_ab_3.name)) == 1

    def test_1_pattern_init_3_runs(self):
        pattern_123_ab = _pattern_3_blocks_1_pre_1_halt(
            "pattern_123_ab", ("1", "2", "3"), (1, 2, 3), "a", "b")

        decider = BoboDecider(
            patterns=[pattern_123_ab],
            event_id_gen=BoboEventIDUnique(),
            run_id_gen=BoboEventIDUnique(),
            max_size=255)

        for i in range(3):
            decider.on_receiver_event(event=_simple(data=1))
            decider.update()
            assert len(decider.runs_from(pattern=pattern_123_ab.name)) == i + 1

    def test_1_pattern_to_completion(self):
        pattern_123_ab = _pattern_3_blocks_1_pre_1_halt(
            "pattern_123_ab", ("1", "2", "3"), (1, 2, 3), "a", "b")

        decider = BoboDecider(
            patterns=[pattern_123_ab],
            event_id_gen=BoboEventIDUnique(),
            run_id_gen=BoboEventIDUnique(),
            max_size=255)

        for event, length in [
            (_simple(data=1), 1),
            (_simple(data=2), 1),
            (_simple(data=3), 0)
        ]:
            decider.on_receiver_event(event=event)
            decider.update()
            assert len(decider.runs_from(
                pattern=pattern_123_ab.name)) == length


class TestInvalid:

    def test_something_invalid(self):
        assert True
