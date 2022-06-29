# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from datetime import datetime
from typing import List, Callable, Tuple

import pytest

from bobocep.engine.decider.bobo_decider import BoboDecider
from bobocep.engine.decider.bobo_decider_run import BoboDeciderRun
from bobocep.engine.decider.bobo_decider_subscriber import \
    BoboDeciderSubscriber
from bobocep.event.bobo_history import BoboHistory
from bobocep.exception.bobo_decider_run_not_found_error import \
    BoboDeciderRunNotFoundError
from bobocep.event.bobo_event_simple import BoboEventSimple
from bobocep.event.event_id.bobo_event_id import BoboEventID
from bobocep.event.event_id.bobo_event_id_unique import BoboEventIDUnique
from bobocep.exception.bobo_key_error import BoboKeyError
from bobocep.exception.bobo_queue_full_error import BoboQueueFullError
from bobocep.pattern.bobo_pattern import BoboPattern
from bobocep.pattern.bobo_pattern_block import BoboPatternBlock
from bobocep.predicate.bobo_predicate_call import BoboPredicateCall
from bobocep.process.bobo_process import BoboProcess


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

    process = BoboProcess(name="process", datagen=lambda p, h: True, patterns=patterns, action=[])

    decider = BoboDecider(
        processes=[process],
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
        self.output: List[Tuple[str, str, BoboHistory]] = []

    def on_decider_completed_run(self,
                                 process_name: str,
                                 pattern_name: str,
                                 history: BoboHistory):
        self.output.append((process_name, pattern_name, history))


class TestValid:

    def test_3_patterns_init(self):
        pattern_123_ab = _pattern_3_blocks_1_pre_1_halt(
            "pattern_123_ab", ("1", "2", "3"), (1, 2, 3), "a", "b")

        pattern_456_cd = _pattern_3_blocks_1_pre_1_halt(
            "pattern_456_cd", ("1", "2", "3"), (4, 5, 6), "c", "d")

        pattern_789_ef = _pattern_3_blocks_1_pre_1_halt(
            "pattern_789_ef", ("1", "2", "3"), (7, 8, 9), "e", "f")

        decider, subscriber = _decsub([
            pattern_123_ab, pattern_456_cd, pattern_789_ef
        ])

        processes = decider.processes()
        assert len(processes) == 1
        assert len(processes[0].patterns) == 3

        assert pattern_123_ab in processes[0].patterns
        assert pattern_456_cd in processes[0].patterns
        assert pattern_789_ef in processes[0].patterns

        assert len(decider.all_runs()) == 0
        assert decider.size() == 0

    def test_3_distinct_patterns_1_run_per_pattern(self):
        pattern_123_ab = _pattern_3_blocks_1_pre_1_halt(
            "pattern_123_ab", ("1", "2", "3"), (1, 2, 3), "a", "b")

        pattern_456_cd = _pattern_3_blocks_1_pre_1_halt(
            "pattern_456_cd", ("1", "2", "3"), (4, 5, 6), "c", "d")

        pattern_789_ef = _pattern_3_blocks_1_pre_1_halt(
            "pattern_789_ef", ("1", "2", "3"), (7, 8, 9), "e", "f")

        decider, subscriber = _decsub([
            pattern_123_ab, pattern_456_cd, pattern_789_ef
        ])

        process_name = decider.processes()[0].name

        for event, pattern in [
            (_simple(data=1), pattern_123_ab),
            (_simple(data=4), pattern_456_cd),
            (_simple(data=7), pattern_789_ef)
        ]:
            decider.on_receiver_event(event=event)
            assert decider.size() == 1

            decider.update()
            assert decider.size() == 0
            assert len(decider.runs_from(process_name, pattern.name)) == 1
            assert decider.runs_from(process_name,
                                     pattern.name)[0].pattern == pattern

    def test_3_patterns_same_blocks(self):
        pattern_123_ab_1 = _pattern_3_blocks_1_pre_1_halt(
            "pattern_123_ab_1", ("1", "2", "3"), (1, 2, 3), "a", "b")

        pattern_123_ab_2 = _pattern_3_blocks_1_pre_1_halt(
            "pattern_123_ab_2", ("1", "2", "3"), (1, 2, 3), "a", "b")

        pattern_123_ab_3 = _pattern_3_blocks_1_pre_1_halt(
            "pattern_123_ab_3", ("1", "2", "3"), (1, 2, 3), "a", "b")

        decider, subscriber = _decsub([
            pattern_123_ab_1, pattern_123_ab_2, pattern_123_ab_3
        ])

        decider.on_receiver_event(event=_simple(data=1))
        decider.update()

        process_name = decider.processes()[0].name

        assert decider.size() == 0
        assert len(decider.all_runs()) == 3
        assert len(decider.runs_from(process_name, pattern_123_ab_1.name)) == 1
        assert len(decider.runs_from(process_name, pattern_123_ab_2.name)) == 1
        assert len(decider.runs_from(process_name, pattern_123_ab_3.name)) == 1

    def test_1_pattern_init_3_runs(self):
        pattern_123_ab = _pattern_3_blocks_1_pre_1_halt(
            "pattern_123_ab", ("1", "2", "3"), (1, 2, 3), "a", "b")

        decider, subscriber = _decsub([pattern_123_ab])
        process_name = decider.processes()[0].name

        for i in range(3):
            decider.on_receiver_event(event=_simple(data=1))
            decider.update()
            assert len(decider.runs_from(process_name,
                                         pattern_123_ab.name)) == i + 1

    def test_1_pattern_to_completion(self):
        pattern_123_ab = _pattern_3_blocks_1_pre_1_halt(
            "pattern_123_ab", ("1", "2", "3"), (1, 2, 3), "a", "b")

        decider, subscriber = _decsub([pattern_123_ab])

        for event, length in [
            (_simple(data=1), 1),
            (_simple(data=2), 1),
            (_simple(data=3), 0)
        ]:
            decider.on_receiver_event(event=event)
            decider.update()

            process_name = decider.processes()[0].name

            assert len(decider.runs_from(
                process_name, pattern_123_ab.name)) == length

        assert len(subscriber.output) == 1

    def test_get_run_from_non_existent_pattern(self):
        pattern_123_ab = _pattern_3_blocks_1_pre_1_halt(
            "pattern_123_ab", ("1", "2", "3"), (1, 2, 3), "a", "b")

        decider, subscriber = _decsub([pattern_123_ab])
        process_name = decider.processes()[0].name

        assert len(decider.runs_from(process_name, "pattern_unknown")) == 0

    def test_1_block_pattern_init_run_immediately_completes(self):
        block_1 = _block("1", call=lambda e, h: e.data == e.data)

        pattern_1 = BoboPattern(
            name="1",
            blocks=[block_1],
            preconditions=[],
            haltconditions=[])

        decider, subscriber = _decsub([pattern_1])

        decider.on_receiver_event(_simple(data=True))
        decider.update()

        assert len(subscriber.output) == 1


class TestInvalid:

    def test_add_on_queue_full(self):
        pattern_123_ab = _pattern_3_blocks_1_pre_1_halt(
            "pattern_123_ab", ("1", "2", "3"), (1, 2, 3), "a", "b")

        decider, subscriber = _decsub([pattern_123_ab], max_size=1)

        decider.on_receiver_event(_simple(data=1))

        with pytest.raises(BoboQueueFullError):
            decider.on_receiver_event(_simple(data=2))

    def test_try_to_remove_run_that_does_not_exist(self):
        pattern_123_ab = _pattern_3_blocks_1_pre_1_halt(
            "pattern_123_ab", ("1", "2", "3"), (1, 2, 3), "a", "b")

        decider, subscriber = _decsub([pattern_123_ab])
        process_name = decider.processes()[0].name

        with pytest.raises(BoboDeciderRunNotFoundError):
            decider._remove_run(process_name=process_name,
                                pattern_name="a",
                                run_id="b")

    def test_duplicate_process_names(self):
        pattern = BoboPattern(
            name="pattern",
            blocks=[_block("1", call=lambda e, h: True)],
            preconditions=[],
            haltconditions=[])

        process_1 = BoboProcess(name="process", datagen=lambda p, h: True, patterns=[pattern], action=[])

        process_2 = BoboProcess(name="process", datagen=lambda p, h: True, patterns=[pattern], action=[])

        with pytest.raises(BoboKeyError):
            BoboDecider(
                processes=[process_1, process_2],
                event_id_gen=BoboEventIDUnique(),
                run_id_gen=BoboEventIDUnique(),
                max_size=255)
