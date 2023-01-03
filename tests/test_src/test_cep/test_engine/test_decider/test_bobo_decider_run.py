# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from src.cep.engine.decider.bobo_decider_run import BoboDeciderRun
from src.cep.event.bobo_event_simple import BoboEventSimple
from src.cep.event.timestamp_gen.bobo_timestamp_gen_epoch import \
    BoboTimestampGenEpoch
from src.cep.process.pattern.bobo_pattern_builder import BoboPatternBuilder
from src.cep.process.pattern.predicate.bobo_predicate_call import \
    BoboPredicateCall


class TestValid:

    def test_pattern_1_block_halt_complete_on_init(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        event = BoboEventSimple("event_id_gen",
                                BoboTimestampGenEpoch().generate(), None)
        run = BoboDeciderRun("run_id", "process_name", pattern, event)

        assert run.is_halted()
        assert run.is_complete()

    def test_pattern_3_blocks_not_halt_not_complete_on_init(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_b", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        event = BoboEventSimple("event_id_gen",
                                BoboTimestampGenEpoch().generate(), None)
        run = BoboDeciderRun("run_id", "process_name", pattern, event)

        assert not run.is_halted()
        assert not run.is_complete()

    def test_pattern_3_blocks_halt_complete_complete(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_b", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a",
                                             BoboTimestampGenEpoch().generate(),
                                             None))

        run.process(
            BoboEventSimple("event_b", BoboTimestampGenEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_c", BoboTimestampGenEpoch().generate(),
                            None))
        assert run.is_halted()
        assert run.is_complete()

    def test_pattern_3_blocks_manual_halt_not_complete(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_b", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a",
                                             BoboTimestampGenEpoch().generate(),
                                             None))

        run.halt()
        assert run.is_halted()
        assert not run.is_complete()

    def test_pattern_3_blocks_process_on_halt(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_b", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a",
                                             BoboTimestampGenEpoch().generate(),
                                             None))

        run.halt()
        run.process(
            BoboEventSimple("event_b", BoboTimestampGenEpoch().generate(),
                            None))
        assert run.is_halted()

    def test_pattern_3_blocks_halt_no_match_on_strict(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .next("group_b", BoboPredicateCall(lambda e, h: False)) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a",
                                             BoboTimestampGenEpoch().generate(),
                                             None))

        run.process(
            BoboEventSimple("event_b", BoboTimestampGenEpoch().generate(),
                            None))
        assert run.is_halted()
        assert not run.is_complete()

    def test_pattern_3_blocks_halt_no_match_on_strict_negated_complete(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .not_next("group_b", BoboPredicateCall(lambda e, h: False)) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a",
                                             BoboTimestampGenEpoch().generate(),
                                             None))

        run.process(
            BoboEventSimple("event_b", BoboTimestampGenEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_c", BoboTimestampGenEpoch().generate(),
                            None))
        assert run.is_halted()
        assert run.is_complete()

    def test_pattern_3_blocks_halt_match_on_strict_negated(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .not_next("group_b", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a",
                                             BoboTimestampGenEpoch().generate(),
                                             None))

        run.process(
            BoboEventSimple("event_b", BoboTimestampGenEpoch().generate(),
                            None))
        assert run.is_halted()
        assert not run.is_complete()

    def test_pattern_3_blocks_not_strict_negated(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a",
                         BoboPredicateCall(lambda e, h: e.data)) \
            .not_followed_by("group_b",
                             BoboPredicateCall(lambda e, h: e.data)) \
            .followed_by("group_c",
                         BoboPredicateCall(lambda e, h: e.data)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a",
                                             BoboTimestampGenEpoch().generate(),
                                             True))

        run.process(
            BoboEventSimple("event_b", BoboTimestampGenEpoch().generate(),
                            True))
        assert not run.is_halted()
        assert not run.is_complete()

    def test_pattern_4_blocks_not_match_optional_complete(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_b", BoboPredicateCall(lambda e, h: False),
                         optional=True) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_d", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a",
                                             BoboTimestampGenEpoch().generate(),
                                             None))

        run.process(
            BoboEventSimple("event_b", BoboTimestampGenEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_c", BoboTimestampGenEpoch().generate(),
                            None))
        assert run.is_halted()
        assert run.is_complete()

    def test_pattern_4_blocks_match_optional_complete(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_b", BoboPredicateCall(lambda e, h: True),
                         optional=True) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_d", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a",
                                             BoboTimestampGenEpoch().generate(),
                                             None))

        run.process(
            BoboEventSimple("event_b", BoboTimestampGenEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_c", BoboTimestampGenEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_d", BoboTimestampGenEpoch().generate(),
                            None))
        assert run.is_halted()
        assert run.is_complete()

    def test_pattern_4_blocks_not_match_optional_then_loop(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_b", BoboPredicateCall(lambda e, h: False),
                         optional=True) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True),
                         loop=True) \
            .followed_by("group_d", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a",
                                             BoboTimestampGenEpoch().generate(),
                                             None))

        run.process(
            BoboEventSimple("event_b", BoboTimestampGenEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_c", BoboTimestampGenEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_d", BoboTimestampGenEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_e", BoboTimestampGenEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

    def test_pattern_4_blocks_match_optional_then_loop(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_b", BoboPredicateCall(lambda e, h: True),
                         optional=True) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True),
                         loop=True) \
            .followed_by("group_d", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a",
                                             BoboTimestampGenEpoch().generate(),
                                             None))

        run.process(
            BoboEventSimple("event_b", BoboTimestampGenEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_c", BoboTimestampGenEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_d", BoboTimestampGenEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_e", BoboTimestampGenEpoch().generate(),
                            None))
        assert not run.is_halted()
        assert not run.is_complete()

    def test_pattern_3_blocks_1_loop_not_match_strict(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: e.data)) \
            .next("group_b", BoboPredicateCall(lambda e, h: e.data),
                  loop=True) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: e.data)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a",
                                             BoboTimestampGenEpoch().generate(),
                                             True))

        run.process(
            BoboEventSimple("event_b", BoboTimestampGenEpoch().generate(),
                            True))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_c", BoboTimestampGenEpoch().generate(),
                            True))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_d", BoboTimestampGenEpoch().generate(),
                            False))
        assert run.is_halted()
        assert not run.is_complete()

    def test_pattern_3_blocks_1_loop_complete(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a",
                         BoboPredicateCall(lambda e, h: e.data == 1)) \
            .followed_by("group_b",
                         BoboPredicateCall(lambda e, h: e.data == 2),
                         loop=True) \
            .followed_by("group_c",
                         BoboPredicateCall(lambda e, h: e.data == 3)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a",
                                             BoboTimestampGenEpoch().generate(),
                                             1))

        run.process(
            BoboEventSimple("event_b", BoboTimestampGenEpoch().generate(), 2))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_c", BoboTimestampGenEpoch().generate(), 2))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_d", BoboTimestampGenEpoch().generate(), 3))
        assert run.is_halted()
        assert run.is_complete()

    def test_pattern_4_blocks_2_loops_complete(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a",
                         BoboPredicateCall(lambda e, h: e.data == 1)) \
            .followed_by("group_b",
                         BoboPredicateCall(lambda e, h: e.data == 2),
                         loop=True) \
            .followed_by("group_c",
                         BoboPredicateCall(lambda e, h: e.data == 3),
                         loop=True) \
            .followed_by("group_d",
                         BoboPredicateCall(lambda e, h: e.data == 4)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a",
                                             BoboTimestampGenEpoch().generate(),
                                             1))

        run.process(
            BoboEventSimple("event_b", BoboTimestampGenEpoch().generate(), 2))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_c", BoboTimestampGenEpoch().generate(), 2))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_d", BoboTimestampGenEpoch().generate(), 3))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_e", BoboTimestampGenEpoch().generate(), 3))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(
            BoboEventSimple("event_f", BoboTimestampGenEpoch().generate(), 4))
        assert run.is_halted()
        assert run.is_complete()
