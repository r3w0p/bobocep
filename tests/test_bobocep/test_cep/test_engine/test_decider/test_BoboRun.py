# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
import pytest

from bobocep.cep.engine.decider.run import BoboRunError
from bobocep.cep.event import BoboEventSimple, BoboHistory
from bobocep.cep.gen.timestamp import BoboGenTimestampEpoch
from bobocep.cep.phenomenon.pattern.builder import BoboPatternBuilder
from tests.test_bobocep.test_cep.test_engine.test_decider import tc_run_simple
from tests.test_bobocep.test_cep.test_event import tc_event_simple
from tests.test_bobocep.test_cep.test_phenomenon import tc_pattern


class TestValid:

    def test_properties(self):
        pattern = tc_pattern(name="pattern_name", data_blocks=[1, 2, 3])
        event = tc_event_simple(event_id="event_id")
        run = tc_run_simple(
            pattern,
            event,
            run_id="run_id",
            phenomenon_name="phenom_name",
            block_index=1)

        assert run.run_id == "run_id"
        assert run.phenomenon_name == "phenom_name"
        assert run.pattern == pattern
        assert run.block_index == 1
        assert run.history().size() == 1
        assert run.history().all_events()[0].event_id == "event_id"
        assert run.is_halted() is False

    def test_set_block(self):
        pattern = tc_pattern(name="pattern_name", data_blocks=[1, 2, 3])
        event_a = tc_event_simple(event_id="event_a")
        event_b = tc_event_simple(event_id="event_b")
        run = tc_run_simple(
            pattern,
            event_a,
            run_id="run_id",
            phenomenon_name="phenom_name",
            block_index=1)

        assert run.block_index == 1
        assert run.history().size() == 1
        assert run.history().all_events()[0].event_id == event_a.event_id
        assert run.is_halted() is False

        run.set_block(2, BoboHistory({
            pattern.blocks[0].group: [event_a],
            pattern.blocks[1].group: [event_b],
        }))

        assert run.block_index == 2
        assert run.history().size() == 2
        assert run.history().all_events()[0].event_id == event_a.event_id
        assert run.history().all_events()[1].event_id == event_b.event_id
        assert run.is_halted() is False

    def test_pattern_1_block_halt_complete_on_init(self):
        pattern = BoboPatternBuilder(name="pattern") \
            .followed_by(lambda e, h: True) \
            .generate()

        run = tc_run_simple(pattern, tc_event_simple("event_a"))

        assert run.is_halted()
        assert run.is_complete()

    def test_pattern_3_blocks_not_halt_not_complete_on_init(self):
        pattern = BoboPatternBuilder(name="pattern") \
            .followed_by(lambda e, h: True) \
            .followed_by(lambda e, h: True) \
            .followed_by(lambda e, h: True) \
            .generate()

        run = tc_run_simple(pattern, tc_event_simple("event_a"))

        assert not run.is_halted()
        assert not run.is_complete()

    def test_pattern_3_blocks_halt_complete_complete(self):
        pattern = BoboPatternBuilder(name="pattern") \
            .followed_by(lambda e, h: True) \
            .followed_by(lambda e, h: True) \
            .followed_by(lambda e, h: True) \
            .generate()

        run = tc_run_simple(pattern, tc_event_simple("event_a"))

        run.process(
            BoboEventSimple("event_b", BoboGenTimestampEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_c", BoboGenTimestampEpoch().generate(),
                            None))
        assert run.is_halted()
        assert run.is_complete()

    def test_pattern_3_blocks_manual_halt_not_complete(self):
        pattern = BoboPatternBuilder(name="pattern") \
            .followed_by(lambda e, h: True) \
            .followed_by(lambda e, h: True) \
            .followed_by(lambda e, h: True) \
            .generate()

        run = tc_run_simple(pattern, tc_event_simple("event_a"))

        run.halt()
        assert run.is_halted()
        assert not run.is_complete()

    def test_pattern_3_blocks_process_on_halt(self):
        pattern = BoboPatternBuilder(name="pattern") \
            .followed_by(lambda e, h: True) \
            .followed_by(lambda e, h: True) \
            .followed_by(lambda e, h: True) \
            .generate()

        run = tc_run_simple(pattern, tc_event_simple("event_a"))

        run.halt()
        run.process(
            BoboEventSimple("event_b", BoboGenTimestampEpoch().generate(),
                            None))
        assert run.is_halted()

    def test_pattern_3_blocks_halt_no_match_on_strict(self):
        pattern = BoboPatternBuilder(name="pattern") \
            .followed_by(lambda e, h: True) \
            .next(lambda e, h: False) \
            .followed_by(lambda e, h: True) \
            .generate()

        run = tc_run_simple(pattern, tc_event_simple("event_a"))

        run.process(
            BoboEventSimple("event_b", BoboGenTimestampEpoch().generate(),
                            None))
        assert run.is_halted()
        assert not run.is_complete()

    def test_pattern_3_blocks_halt_no_match_on_strict_negated_complete(self):
        pattern = BoboPatternBuilder(name="pattern") \
            .followed_by(lambda e, h: True) \
            .not_next(lambda e, h: False) \
            .followed_by(lambda e, h: True) \
            .generate()

        run = tc_run_simple(pattern, tc_event_simple("event_a"))

        run.process(
            BoboEventSimple("event_b", BoboGenTimestampEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_c", BoboGenTimestampEpoch().generate(),
                            None))
        assert run.is_halted()
        assert run.is_complete()

    def test_pattern_3_blocks_halt_match_on_strict_negated(self):
        pattern = BoboPatternBuilder(name="pattern") \
            .followed_by(lambda e, h: True) \
            .not_next(lambda e, h: True) \
            .followed_by(lambda e, h: True) \
            .generate()

        run = tc_run_simple(pattern, tc_event_simple("event_a"))

        run.process(
            BoboEventSimple("event_b", BoboGenTimestampEpoch().generate(),
                            None))
        assert run.is_halted()
        assert not run.is_complete()

    def test_pattern_3_blocks_not_strict_negated(self):
        pattern = BoboPatternBuilder(name="pattern") \
            .followed_by(lambda e, h: e.data) \
            .not_followed_by(lambda e, h: e.data) \
            .followed_by(lambda e, h: e.data) \
            .generate()

        run = tc_run_simple(pattern, tc_event_simple("event_a", data=True))

        run.process(
            BoboEventSimple("event_b", BoboGenTimestampEpoch().generate(),
                            True))
        assert not run.is_halted()
        assert not run.is_complete()

    def test_pattern_4_blocks_not_match_optional_complete(self):
        pattern = BoboPatternBuilder(name="pattern") \
            .followed_by(lambda e, h: True) \
            .followed_by(lambda e, h: False,
                         optional=True) \
            .followed_by(lambda e, h: True) \
            .followed_by(lambda e, h: True) \
            .generate()

        run = tc_run_simple(pattern, tc_event_simple("event_a"))

        run.process(
            BoboEventSimple("event_b", BoboGenTimestampEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_c", BoboGenTimestampEpoch().generate(),
                            None))
        assert run.is_halted()
        assert run.is_complete()

    def test_pattern_4_blocks_match_optional_complete(self):
        pattern = BoboPatternBuilder(name="pattern") \
            .followed_by(lambda e, h: True) \
            .followed_by(lambda e, h: True,
                         optional=True) \
            .followed_by(lambda e, h: True) \
            .followed_by(lambda e, h: True) \
            .generate()

        run = tc_run_simple(pattern, tc_event_simple("event_a"))

        run.process(
            BoboEventSimple("event_b", BoboGenTimestampEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_c", BoboGenTimestampEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_d", BoboGenTimestampEpoch().generate(),
                            None))
        assert run.is_halted()
        assert run.is_complete()

    def test_pattern_4_blocks_not_match_optional_then_loop(self):
        pattern = BoboPatternBuilder(name="pattern") \
            .followed_by(lambda e, h: True) \
            .followed_by(lambda e, h: False,
                         optional=True) \
            .followed_by(lambda e, h: True,
                         loop=True) \
            .followed_by(lambda e, h: True) \
            .generate()

        run = tc_run_simple(pattern, tc_event_simple("event_a"))

        run.process(
            BoboEventSimple("event_b", BoboGenTimestampEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_c", BoboGenTimestampEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_d", BoboGenTimestampEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_e", BoboGenTimestampEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

    def test_pattern_4_blocks_match_optional_then_loop(self):
        pattern = BoboPatternBuilder(name="pattern") \
            .followed_by(lambda e, h: True) \
            .followed_by(lambda e, h: True,
                         optional=True) \
            .followed_by(lambda e, h: True,
                         loop=True) \
            .followed_by(lambda e, h: True) \
            .generate()

        run = tc_run_simple(pattern, tc_event_simple("event_a"))

        run.process(
            BoboEventSimple("event_b", BoboGenTimestampEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_c", BoboGenTimestampEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_d", BoboGenTimestampEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_e", BoboGenTimestampEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

    def test_pattern_3_blocks_1_loop_not_match_strict(self):
        pattern = BoboPatternBuilder(name="pattern") \
            .followed_by(lambda e, h: e.data) \
            .next(lambda e, h: e.data, loop=True) \
            .followed_by(lambda e, h: e.data) \
            .generate()

        run = tc_run_simple(pattern, tc_event_simple("event_a", data=True))

        run.process(
            BoboEventSimple("event_b", BoboGenTimestampEpoch().generate(),
                            True))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_c", BoboGenTimestampEpoch().generate(),
                            True))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_d", BoboGenTimestampEpoch().generate(),
                            False))
        assert run.is_halted()
        assert not run.is_complete()

    def test_pattern_3_blocks_1_loop_complete(self):
        pattern = BoboPatternBuilder(name="pattern") \
            .followed_by(lambda e, h: e.data == 1) \
            .followed_by(lambda e, h: e.data == 2, loop=True) \
            .followed_by(lambda e, h: e.data == 3) \
            .generate()

        run = tc_run_simple(pattern, tc_event_simple("event_a", data=1))

        run.process(
            BoboEventSimple("event_b", BoboGenTimestampEpoch().generate(), 2))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_c", BoboGenTimestampEpoch().generate(), 2))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_d", BoboGenTimestampEpoch().generate(), 3))
        assert run.is_halted()
        assert run.is_complete()

    def test_pattern_4_blocks_2_loops_complete(self):
        pattern = BoboPatternBuilder(name="pattern") \
            .followed_by(lambda e, h: e.data == 1) \
            .followed_by(lambda e, h: e.data == 2, loop=True) \
            .followed_by(lambda e, h: e.data == 3, loop=True) \
            .followed_by(lambda e, h: e.data == 4) \
            .generate()

        run = tc_run_simple(pattern, tc_event_simple("event_a", data=1))

        run.process(
            BoboEventSimple("event_b", BoboGenTimestampEpoch().generate(), 2))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_c", BoboGenTimestampEpoch().generate(), 2))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_d", BoboGenTimestampEpoch().generate(), 3))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_e", BoboGenTimestampEpoch().generate(), 3))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_f", BoboGenTimestampEpoch().generate(), 4))
        assert run.is_halted()
        assert run.is_complete()

    def test_history(self):
        pattern = BoboPatternBuilder(name="pattern") \
            .followed_by(lambda e, h: True, group="group_a") \
            .followed_by(lambda e, h: True, group="group_b") \
            .followed_by(lambda e, h: True, group="group_c") \
            .generate()

        event_a = tc_event_simple("event_a")
        event_b = tc_event_simple("event_b")

        run = tc_run_simple(pattern, event_a)
        run.process(event_b)

        history = run.history()

        group_a = history.group("group_a")
        assert len(group_a) == 1
        assert group_a[0].event_id == event_a.event_id

        group_b = history.group("group_b")
        assert len(group_b) == 1
        assert group_b[0].event_id == event_b.event_id


class TestInvalid:

    def test_length_0_run_id(self):
        with pytest.raises(BoboRunError):
            tc_run_simple(tc_pattern(), tc_event_simple(), run_id="")

    def test_length_0_phenomenon_name(self):
        with pytest.raises(BoboRunError):
            tc_run_simple(tc_pattern(), tc_event_simple(), phenomenon_name="")

    def test_block_index_zero(self):
        with pytest.raises(BoboRunError):
            tc_run_simple(tc_pattern(), tc_event_simple(), block_index=0)

    def test_block_index_negative(self):
        with pytest.raises(BoboRunError):
            tc_run_simple(
                tc_pattern(),
                tc_event_simple(),
                block_index=-1)

    def test_history_no_events(self):
        with pytest.raises(BoboRunError):
            tc_run_simple(
                tc_pattern(),
                tc_event_simple(),
                history=BoboHistory({}))

    def test_set_block_block_index_zero(self):
        pattern = tc_pattern(name="pattern_name", data_blocks=[1, 2, 3])
        event_a = tc_event_simple(event_id="event_a")
        event_b = tc_event_simple(event_id="event_b")
        run = tc_run_simple(
            tc_pattern(),
            tc_event_simple(),
            run_id="run_id",
            phenomenon_name="phenom_name",
            block_index=1)

        with pytest.raises(BoboRunError):
            run.set_block(0, BoboHistory({
                pattern.blocks[0].group: [event_a],
                pattern.blocks[1].group: [event_b],
            }))

    def test_set_block_block_index_negative(self):
        pattern = tc_pattern(name="pattern_name", data_blocks=[1, 2, 3])
        event_a = tc_event_simple(event_id="event_a")
        event_b = tc_event_simple(event_id="event_b")
        run = tc_run_simple(
            tc_pattern(),
            tc_event_simple(),
            run_id="run_id",
            phenomenon_name="phenom_name",
            block_index=1)

        with pytest.raises(BoboRunError):
            run.set_block(-1, BoboHistory({
                pattern.blocks[0].group: [event_a],
                pattern.blocks[1].group: [event_b],
            }))
