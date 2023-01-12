# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import tests.common as tc
from bobocep.cep.engine.task.decider import BoboDeciderRun
from bobocep.cep.event import BoboEventSimple
from bobocep.cep.gen.timestamp import BoboGenTimestampEpoch
from bobocep.cep.process.pattern.builder import BoboPatternBuilder
from bobocep.cep.process.pattern.predicate import BoboPredicateCall


class TestValid:

    def test_pattern_1_block_halt_complete_on_init(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        run = BoboDeciderRun(
            "run_id", "process_name", pattern,
            tc.event_simple("event_a"))

        assert run.is_halted()
        assert run.is_complete()

    def test_pattern_3_blocks_not_halt_not_complete_on_init(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_b", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        run = BoboDeciderRun(
            "run_id", "process_name", pattern,
            tc.event_simple("event_a"))

        assert not run.is_halted()
        assert not run.is_complete()

    def test_pattern_3_blocks_halt_complete_complete(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_b", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        run = BoboDeciderRun(
            "run_id", "process_name", pattern,
            tc.event_simple("event_a"))

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

        run = BoboDeciderRun(
            "run_id", "process_name", pattern,
            tc.event_simple("event_a"))

        run.halt()
        assert run.is_halted()
        assert not run.is_complete()

    def test_pattern_3_blocks_process_on_halt(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_b", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        run = BoboDeciderRun(
            "run_id", "process_name", pattern,
            tc.event_simple("event_a"))

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

        run = BoboDeciderRun(
            "run_id", "process_name", pattern,
            tc.event_simple("event_a"))

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

        run = BoboDeciderRun(
            "run_id", "process_name", pattern,
            tc.event_simple("event_a"))

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

        run = BoboDeciderRun(
            "run_id", "process_name", pattern,
            tc.event_simple("event_a"))

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

        run = BoboDeciderRun(
            "run_id", "process_name", pattern,
            tc.event_simple("event_a", data=True))

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

        run = BoboDeciderRun(
            "run_id", "process_name", pattern,
            tc.event_simple("event_a"))

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

        run = BoboDeciderRun(
            "run_id", "process_name", pattern,
            tc.event_simple("event_a"))

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

        run = BoboDeciderRun(
            "run_id", "process_name", pattern,
            tc.event_simple("event_a"))

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

        run = BoboDeciderRun(
            "run_id", "process_name", pattern,
            tc.event_simple("event_a"))

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

        run = BoboDeciderRun(
            "run_id", "process_name", pattern,
            tc.event_simple("event_a", data=True))

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

        run = BoboDeciderRun(
            "run_id", "process_name", pattern,
            tc.event_simple("event_a", data=1))

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

        run = BoboDeciderRun(
            "run_id", "process_name", pattern,
            tc.event_simple("event_a", data=1))

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
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_b", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        event_a = tc.event_simple("event_a")
        event_b = tc.event_simple("event_b")

        run = BoboDeciderRun("run_id", "process_name", pattern, event_a)
        run.process(event_b)

        history = run.history()

        group_a = history.group("group_a")
        assert len(group_a) == 1
        assert group_a[0].event_id == event_a.event_id

        group_b = history.group("group_b")
        assert len(group_b) == 1
        assert group_b[0].event_id == event_b.event_id
