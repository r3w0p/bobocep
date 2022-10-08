# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from datetime import datetime

from bobocep.cep.engine.decider.bobo_decider_run import BoboDeciderRun
from bobocep.cep.event.bobo_event_simple import BoboEventSimple
from bobocep.cep.process.pattern.bobo_pattern_builder import BoboPatternBuilder
from bobocep.cep.process.pattern.predicate.bobo_predicate_call import \
    BoboPredicateCall


class TestValid:

    def test_pattern_1_block_halt_complete_on_init(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        event = BoboEventSimple("event_id_gen", datetime.now(), None)
        run = BoboDeciderRun("run_id", "process_name", pattern, event)

        assert run.is_halted()
        assert run.is_complete()

    def test_pattern_3_blocks_not_halt_not_complete_on_init(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_b", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        event = BoboEventSimple("event_id_gen", datetime.now(), None)
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
                             BoboEventSimple("event_a", datetime.now(), None))

        run.process(BoboEventSimple("event_b", datetime.now(), None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(BoboEventSimple("event_c", datetime.now(), None))
        assert run.is_halted()
        assert run.is_complete()

    def test_pattern_3_blocks_manual_halt_not_complete(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_b", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a", datetime.now(), None))

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
                             BoboEventSimple("event_a", datetime.now(), None))

        run.halt()
        run.process(BoboEventSimple("event_b", datetime.now(), None))
        assert run.is_halted()

    def test_pattern_3_blocks_halt_no_match_on_strict(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .next("group_b", BoboPredicateCall(lambda e, h: False)) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a", datetime.now(), None))

        run.process(BoboEventSimple("event_b", datetime.now(), None))
        assert run.is_halted()
        assert not run.is_complete()

    def test_pattern_3_blocks_halt_no_match_on_strict_negated_complete(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .not_next("group_b", BoboPredicateCall(lambda e, h: False)) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a", datetime.now(), None))

        run.process(BoboEventSimple("event_b", datetime.now(), None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(BoboEventSimple("event_c", datetime.now(), None))
        assert run.is_halted()
        assert run.is_complete()

    def test_pattern_3_blocks_halt_match_on_strict_negated(self):
        pattern = BoboPatternBuilder() \
            .followed_by("group_a", BoboPredicateCall(lambda e, h: True)) \
            .not_next("group_b", BoboPredicateCall(lambda e, h: True)) \
            .followed_by("group_c", BoboPredicateCall(lambda e, h: True)) \
            .generate("pattern")

        run = BoboDeciderRun("run_id", "process_name", pattern,
                             BoboEventSimple("event_a", datetime.now(), None))

        run.process(BoboEventSimple("event_b", datetime.now(), None))
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
                             BoboEventSimple("event_a", datetime.now(), True))

        run.process(BoboEventSimple("event_b", datetime.now(), True))
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
                             BoboEventSimple("event_a", datetime.now(), None))

        run.process(BoboEventSimple("event_b", datetime.now(), None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(BoboEventSimple("event_c", datetime.now(), None))
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
                             BoboEventSimple("event_a", datetime.now(), None))

        run.process(BoboEventSimple("event_b", datetime.now(), None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(BoboEventSimple("event_c", datetime.now(), None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(BoboEventSimple("event_d", datetime.now(), None))
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
                             BoboEventSimple("event_a", datetime.now(), None))

        run.process(BoboEventSimple("event_b", datetime.now(), None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(BoboEventSimple("event_c", datetime.now(), None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(BoboEventSimple("event_d", datetime.now(), None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(BoboEventSimple("event_e", datetime.now(), None))
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
                             BoboEventSimple("event_a", datetime.now(), None))

        run.process(BoboEventSimple("event_b", datetime.now(), None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(BoboEventSimple("event_c", datetime.now(), None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(BoboEventSimple("event_d", datetime.now(), None))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(BoboEventSimple("event_e", datetime.now(), None))
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
                             BoboEventSimple("event_a", datetime.now(), True))

        run.process(BoboEventSimple("event_b", datetime.now(), True))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(BoboEventSimple("event_c", datetime.now(), True))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(BoboEventSimple("event_d", datetime.now(), False))
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
                             BoboEventSimple("event_a", datetime.now(), 1))

        run.process(BoboEventSimple("event_b", datetime.now(), 2))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(BoboEventSimple("event_c", datetime.now(), 2))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(BoboEventSimple("event_d", datetime.now(), 3))
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
                             BoboEventSimple("event_a", datetime.now(), 1))

        run.process(BoboEventSimple("event_b", datetime.now(), 2))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(BoboEventSimple("event_c", datetime.now(), 2))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(BoboEventSimple("event_d", datetime.now(), 3))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(BoboEventSimple("event_e", datetime.now(), 3))
        assert not run.is_halted()
        assert not run.is_complete()

        run.process(BoboEventSimple("event_f", datetime.now(), 4))
        assert run.is_halted()
        assert run.is_complete()
