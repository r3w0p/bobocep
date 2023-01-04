# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from bobocep.cep.engine.decider.bobo_decider_run import BoboDeciderRun
from bobocep.cep.event.bobo_event_simple import BoboEventSimple
from bobocep.cep.gen.timestamp.bobo_gen_timestamp_epoch import \
    BoboGenTimestampEpoch
from bobocep.cep.process.pattern.bobo_pattern_builder import BoboPatternBuilder
from bobocep.cep.process.pattern.predicate.bobo_predicate_call import \
    BoboPredicateCall


class TestValid:

    def test_pattern_1_block_halt_complete_on_init(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        event = BoboEventSimple("event_id",
                                BoboGenTimestampEpoch().generate(), None)
        run = BoboDeciderRun("run_id", "process_name", pattern, event)

        assert run.is_halted()
        assert run.is_complete()

    def test_pattern_3_blocks_not_halt_not_complete_on_init(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_b", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        event = BoboEventSimple("event_id",
                                BoboGenTimestampEpoch().generate(), None)
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
                                             BoboGenTimestampEpoch().generate(),
                                             None))

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
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_b", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a",
                                             BoboGenTimestampEpoch().generate(),
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
                                             BoboGenTimestampEpoch().generate(),
                                             None))

        run.halt()
        run.process(
            BoboEventSimple("event_b", BoboGenTimestampEpoch().generate(),
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
                                             BoboGenTimestampEpoch().generate(),
                                             None))

        run.process(
            BoboEventSimple("event_b", BoboGenTimestampEpoch().generate(),
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
                                             BoboGenTimestampEpoch().generate(),
                                             None))

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
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .not_next("group_b", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a",
                                             BoboGenTimestampEpoch().generate(),
                                             None))

        run.process(
            BoboEventSimple("event_b", BoboGenTimestampEpoch().generate(),
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
                                             BoboGenTimestampEpoch().generate(),
                                             True))

        run.process(
            BoboEventSimple("event_b", BoboGenTimestampEpoch().generate(),
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
                                             BoboGenTimestampEpoch().generate(),
                                             None))

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
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_b", BoboPredicateCall(lambda e, h: True),
                         optional=True) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_d", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a",
                                             BoboGenTimestampEpoch().generate(),
                                             None))

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
                                             BoboGenTimestampEpoch().generate(),
                                             None))

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
                                             BoboGenTimestampEpoch().generate(),
                                             None))

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
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: e.data)) \
            .next("group_b", BoboPredicateCall(lambda e, h: e.data),
                  loop=True) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: e.data)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a",
                                             BoboGenTimestampEpoch().generate(),
                                             True))

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
                                             BoboGenTimestampEpoch().generate(),
                                             1))

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
                                             BoboGenTimestampEpoch().generate(),
                                             1))

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
