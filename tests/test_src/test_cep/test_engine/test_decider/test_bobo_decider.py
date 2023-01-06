# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

import tests.common as tc
from bobocep.cep.engine.decider.bobo_decider import BoboDecider
from bobocep.cep.engine.decider.bobo_decider_error import \
    BoboDeciderError
from bobocep.cep.gen.event_id.bobo_gen_event_id_unique import \
    BoboGenEventIDUnique


class TestValid:

    def test_3_patterns_init(self):
        pattern_123 = tc.pattern("pattern_123", data_blocks=[1, 2, 3])
        pattern_456 = tc.pattern("pattern_456", data_blocks=[4, 5, 6])
        pattern_789 = tc.pattern("pattern_789", data_blocks=[7, 8, 9])

        decider, subscriber = tc.decider_sub([
            tc.process(patterns=[pattern_123, pattern_456, pattern_789])
        ])

        processes = decider.processes()
        assert len(processes) == 1
        assert len(processes[0].patterns) == 3

        assert pattern_123 in processes[0].patterns
        assert pattern_456 in processes[0].patterns
        assert pattern_789 in processes[0].patterns

        assert len(decider.all_runs()) == 0
        assert decider.size() == 0

    def test_3_distinct_patterns_1_run_per_pattern(self):
        pattern_123 = tc.pattern("pattern_123", data_blocks=[1, 2, 3])
        pattern_456 = tc.pattern("pattern_456", data_blocks=[4, 5, 6])
        pattern_789 = tc.pattern("pattern_789", data_blocks=[7, 8, 9])

        decider, subscriber = tc.decider_sub([
            tc.process(patterns=[pattern_123, pattern_456, pattern_789])
        ])

        process_name = decider.processes()[0].name

        for event, pattern in [
            (tc.event_simple(data=1), pattern_123),
            (tc.event_simple(data=4), pattern_456),
            (tc.event_simple(data=7), pattern_789)
        ]:
            decider.on_receiver_update(event=event)
            assert decider.size() == 1

            result_update = decider.update()
            assert result_update is True
            assert decider.size() == 0
            assert len(decider.runs_from(process_name, pattern.name)) == 1
            assert decider.runs_from(process_name,
                                     pattern.name)[0].pattern == pattern

    def test_3_patterns_same_blocks(self):
        pattern_123_1 = tc.pattern("pattern_123_1", data_blocks=[1, 2, 3])
        pattern_123_2 = tc.pattern("pattern_123_2", data_blocks=[1, 2, 3])
        pattern_123_3 = tc.pattern("pattern_123_3", data_blocks=[1, 2, 3])

        decider, subscriber = tc.decider_sub([
            tc.process(patterns=[pattern_123_1, pattern_123_2, pattern_123_3])
        ])

        decider.on_receiver_update(event=tc.event_simple(data=1))
        result_update = decider.update()

        process_name = decider.processes()[0].name

        assert result_update is True
        assert decider.size() == 0
        assert len(decider.all_runs()) == 3
        assert len(decider.runs_from(process_name, pattern_123_1.name)) == 1
        assert len(decider.runs_from(process_name, pattern_123_2.name)) == 1
        assert len(decider.runs_from(process_name, pattern_123_3.name)) == 1

    def test_1_pattern_init_3_runs(self):
        pattern_123 = tc.pattern(data_blocks=[1, 2, 3])
        process = tc.process(patterns=[pattern_123])

        decider, subscriber = tc.decider_sub([process])
        process_name = decider.processes()[0].name

        for i in range(3):
            decider.on_receiver_update(event=tc.event_simple(data=1))
            result_update = decider.update()
            assert result_update is True
            assert len(decider.runs_from(process_name,
                                         pattern_123.name)) == i + 1

    def test_1_pattern_to_completion(self):
        pattern_123 = tc.pattern(data_blocks=[1, 2, 3])
        process = tc.process(patterns=[pattern_123])

        decider, subscriber = tc.decider_sub([process])

        for event, length in [
            (tc.event_simple(data=1), 1),
            (tc.event_simple(data=2), 1),
            (tc.event_simple(data=3), 0)
        ]:
            decider.on_receiver_update(event=event)
            result_update = decider.update()

            process_name = decider.processes()[0].name

            assert result_update is True
            assert len(decider.runs_from(
                process_name, pattern_123.name)) == length

        assert len(subscriber.halted_complete) == 1

    def test_get_run_from_non_existent_pattern(self):
        pattern_123 = tc.pattern(data_blocks=[1, 2, 3])
        process = tc.process(patterns=[pattern_123])

        decider, subscriber = tc.decider_sub([process])
        process_name = decider.processes()[0].name

        assert len(decider.runs_from(process_name, "pattern_unknown")) == 0

    def test_1_block_pattern_init_run_immediately_completes(self):
        pattern = tc.pattern(
            data_blocks=[1],
            data_pres=[],
            data_halts=[])

        decider, subscriber = tc.decider_sub([tc.process(patterns=[pattern])])

        decider.on_receiver_update(tc.event_simple(data=1))
        result_update = decider.update()

        assert result_update is True
        assert len(subscriber.halted_complete) == 1

    def test_close_then_update(self):
        decider, subscriber = tc.decider_sub([tc.process()])

        decider.close()
        assert decider.is_closed()
        assert decider.update() is False

    def test_close_then_on_receiver_update(self):
        decider, subscriber = tc.decider_sub([tc.process()])

        decider.close()
        assert decider.is_closed()
        assert decider.size() == 0

        decider.on_receiver_update(tc.event_simple())
        assert decider.size() == 0


class TestInvalid:

    def test_add_on_queue_full(self):
        process = tc.process(patterns=[tc.pattern(data_blocks=[1, 2, 3])])
        decider, subscriber = tc.decider_sub([process], max_size=1)

        decider.on_receiver_update(tc.event_simple(data=1))

        with pytest.raises(BoboDeciderError):
            decider.on_receiver_update(tc.event_simple(data=2))

    def test_try_to_remove_run_that_does_not_exist(self):
        process = tc.process(patterns=[tc.pattern(data_blocks=[1, 2, 3])])
        decider, subscriber = tc.decider_sub([process])
        process_name = decider.processes()[0].name

        with pytest.raises(BoboDeciderError):
            decider._remove_run(process_name=process_name,
                                pattern_name="a",
                                run_id="b")

    def test_duplicate_process_names(self):
        with pytest.raises(BoboDeciderError):
            BoboDecider(
                processes=[tc.process(patterns=[tc.pattern()]),
                           tc.process(patterns=[tc.pattern()])],
                gen_event_id=BoboGenEventIDUnique(),
                gen_run_id=BoboGenEventIDUnique(),
                max_size=255)

    def test_duplicate_run_id_for_pattern(self):
        process = tc.process(patterns=[tc.pattern(data_blocks=[1, 2, 3])])

        decider, subscriber = tc.decider_sub(
            [process],
            run_id_gen=tc.BoboSameEveryTimeEventID())

        decider.on_receiver_update(event=tc.event_simple(data=1))
        result_update = decider.update()
        assert result_update is True

        decider.on_receiver_update(event=tc.event_simple(data=1))

        with pytest.raises(BoboDeciderError):
            decider.update()
