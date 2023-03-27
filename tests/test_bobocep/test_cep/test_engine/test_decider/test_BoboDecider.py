# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

import tests.common as tc
from bobocep.cep.engine.decider import BoboDeciderError, BoboDecider, BoboRun
from bobocep.cep.gen.event_id import BoboGenEventIDUnique
from bobocep.cep.phenomenon.pattern.builder import BoboPatternBuilder
from bobocep.cep.phenomenon.pattern.predicate import BoboPredicateCall


class TestValid:

    def test_3_patterns_init(self):
        pattern_123 = tc.pattern("pattern_123", data_blocks=[1, 2, 3])
        pattern_456 = tc.pattern("pattern_456", data_blocks=[4, 5, 6])
        pattern_789 = tc.pattern("pattern_789", data_blocks=[7, 8, 9])

        decider, subscriber = tc.decider_sub([
            tc.phenomenon(patterns=[pattern_123, pattern_456, pattern_789])
        ])

        phenomena = decider.phenomena()
        assert len(phenomena) == 1
        assert len(phenomena[0].patterns) == 3

        assert pattern_123 in phenomena[0].patterns
        assert pattern_456 in phenomena[0].patterns
        assert pattern_789 in phenomena[0].patterns

        assert len(decider.all_runs()) == 0
        assert decider.size() == 0

    def test_3_distinct_patterns_1_run_per_pattern(self):
        pattern_123 = tc.pattern("pattern_123", data_blocks=[1, 2, 3])
        pattern_456 = tc.pattern("pattern_456", data_blocks=[4, 5, 6])
        pattern_789 = tc.pattern("pattern_789", data_blocks=[7, 8, 9])

        decider, subscriber = tc.decider_sub([
            tc.phenomenon(patterns=[pattern_123, pattern_456, pattern_789])
        ])

        phenomenon_name = decider.phenomena()[0].name

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
            assert len(decider.runs_from(phenomenon_name, pattern.name)) == 1
            assert decider.runs_from(phenomenon_name,
                                     pattern.name)[0].pattern == pattern

    def test_3_patterns_same_blocks(self):
        pattern_123_1 = tc.pattern("pattern_123_1", data_blocks=[1, 2, 3])
        pattern_123_2 = tc.pattern("pattern_123_2", data_blocks=[1, 2, 3])
        pattern_123_3 = tc.pattern("pattern_123_3", data_blocks=[1, 2, 3])

        decider, subscriber = tc.decider_sub([
            tc.phenomenon(patterns=[pattern_123_1, pattern_123_2, pattern_123_3])
        ])

        decider.on_receiver_update(event=tc.event_simple(data=1))
        result_update = decider.update()

        phenomenon_name = decider.phenomena()[0].name

        assert result_update is True
        assert decider.size() == 0
        assert len(decider.all_runs()) == 3
        assert len(decider.runs_from(phenomenon_name, pattern_123_1.name)) == 1
        assert len(decider.runs_from(phenomenon_name, pattern_123_2.name)) == 1
        assert len(decider.runs_from(phenomenon_name, pattern_123_3.name)) == 1

    def test_1_pattern_init_3_runs(self):
        pattern_123 = tc.pattern(data_blocks=[1, 2, 3])
        phenomenon = tc.phenomenon(patterns=[pattern_123])

        decider, subscriber = tc.decider_sub([phenomenon])
        phenom_name = decider.phenomena()[0].name

        for i in range(3):
            decider.on_receiver_update(event=tc.event_simple(data=1))
            result_update = decider.update()
            assert result_update is True
            assert len(decider.runs_from(phenom_name,
                                         pattern_123.name)) == i + 1

    def test_1_pattern_to_completion(self):
        pattern_123 = tc.pattern(data_blocks=[1, 2, 3])
        phenom = tc.phenomenon(patterns=[pattern_123])

        decider, subscriber = tc.decider_sub([phenom])

        for event, length in [
            (tc.event_simple(data=1), 1),
            (tc.event_simple(data=2), 1),
            (tc.event_simple(data=3), 0)
        ]:
            decider.on_receiver_update(event=event)
            result_update = decider.update()

            phenom_name = decider.phenomena()[0].name

            assert result_update is True
            assert len(decider.runs_from(
                phenom_name, pattern_123.name)) == length

        assert len(subscriber.completed) == 1

    def test_get_run_from_non_existent_pattern(self):
        pattern_123 = tc.pattern(data_blocks=[1, 2, 3])
        phenom = tc.phenomenon(patterns=[pattern_123])

        decider, subscriber = tc.decider_sub([phenom])
        phenom_name = decider.phenomena()[0].name

        assert len(decider.runs_from(phenom_name, "pattern_unknown")) == 0

    def test_1_block_pattern_init_run_immediately_completes(self):
        pattern = tc.pattern(
            data_blocks=[1],
            data_pres=[],
            data_halts=[])

        decider, subscriber = tc.decider_sub([tc.phenomenon(patterns=[pattern])])

        decider.on_receiver_update(tc.event_simple(data=1))
        result_update = decider.update()

        assert result_update is True
        assert len(subscriber.completed) == 1

    def test_3_block_pattern_halt_incomplete_triggered_haltcondition(self):
        pattern = tc.pattern(
            data_blocks=[1, 2, 3],
            data_pres=[],
            data_halts=[5])

        decider, subscriber = tc.decider_sub([tc.phenomenon(patterns=[pattern])])

        decider.on_receiver_update(tc.event_simple(data=1))
        decider.update()
        assert len(subscriber.halted) == 0

        decider.on_receiver_update(tc.event_simple(data=2))
        decider.update()
        assert len(subscriber.halted) == 0

        decider.on_receiver_update(tc.event_simple(data=5))
        decider.update()
        assert len(subscriber.halted) == 1

    def test_3_block_pattern_halt_incomplete_failed_precondition(self):
        pattern = BoboPatternBuilder() \
            .next("g1", BoboPredicateCall(lambda e, h: e.data == 10)) \
            .next("g2", BoboPredicateCall(lambda e, h: e.data == 11)) \
            .next("g3", BoboPredicateCall(lambda e, h: e.data == 12)) \
            .precondition(BoboPredicateCall(lambda e, h: e.data > 9)) \
            .generate("pattern")

        decider, subscriber = tc.decider_sub([tc.phenomenon(patterns=[pattern])])

        decider.on_receiver_update(tc.event_simple(data=10))
        decider.update()
        assert len(subscriber.halted) == 0

        decider.on_receiver_update(tc.event_simple(data=11))
        decider.update()
        assert len(subscriber.halted) == 0

        decider.on_receiver_update(tc.event_simple(data=5))
        decider.update()
        assert len(subscriber.halted) == 1

    def test_close_then_update(self):
        decider, subscriber = tc.decider_sub([tc.phenomenon()])

        decider.close()
        assert decider.is_closed()
        assert decider.update() is False

    def test_close_then_on_receiver_update(self):
        decider, subscriber = tc.decider_sub([tc.phenomenon()])

        decider.close()
        assert decider.is_closed()
        assert decider.size() == 0

        decider.on_receiver_update(tc.event_simple())
        assert decider.size() == 0


class TestInvalid:

    def test_add_on_queue_full(self):
        phenom = tc.phenomenon(patterns=[tc.pattern(data_blocks=[1, 2, 3])])
        decider, subscriber = tc.decider_sub([phenom], max_size=1)

        decider.on_receiver_update(tc.event_simple(data=1))

        with pytest.raises(BoboDeciderError):
            decider.on_receiver_update(tc.event_simple(data=2))

    def test_try_to_remove_run_that_does_not_exist(self):
        phenom = tc.phenomenon(patterns=[tc.pattern(data_blocks=[1, 2, 3])])
        decider, subscriber = tc.decider_sub([phenom])
        phenom_name = decider.phenomena()[0].name

        with pytest.raises(BoboDeciderError):
            decider._remove_run(phenomenon_name=phenom_name,
                                pattern_name="a",
                                run_id="b")

    def test_duplicate_phenomena_names(self):
        with pytest.raises(BoboDeciderError):
            BoboDecider(
                phenomena=[tc.phenomenon(patterns=[tc.pattern()]),
                           tc.phenomenon(patterns=[tc.pattern()])],
                gen_event_id=BoboGenEventIDUnique(),
                gen_run_id=BoboGenEventIDUnique(),
                max_size=255)

    def test_duplicate_run_id_for_pattern(self):
        phenom = tc.phenomenon(patterns=[tc.pattern(data_blocks=[1, 2, 3])])

        decider, subscriber = tc.decider_sub(
            [phenom],
            run_id_gen=tc.BoboSameEveryTimeEventID())

        decider.on_receiver_update(event=tc.event_simple(data=1))
        result_update = decider.update()
        assert result_update is True

        decider.on_receiver_update(event=tc.event_simple(data=1))

        with pytest.raises(BoboDeciderError):
            decider.update()

    def test_run_at(self):
        pattern = tc.pattern(name="pattern", data_blocks=[1, 2, 3])
        phenomenon = tc.phenomenon(name="phenomenon", patterns=[pattern])

        decider, subscriber = tc.decider_sub([phenomenon])

        decider.on_receiver_update(event=tc.event_simple(data=1))
        assert decider.update()

        all_runs = decider.runs_from(phenomenon.name, pattern.name)
        assert len(all_runs) == 1

        run = decider.run_at(phenomenon.name, pattern.name, all_runs[0].run_id)
        assert run is not None

        assert run.phenomenon_name == phenomenon.name
        assert run.pattern.name == pattern.name

    def test_snapshot_decider_closed(self):
        pattern = tc.pattern(
            name="pattern",
            data_blocks=[1, 2, 3],
            data_halts=[4])
        phenomenon = tc.phenomenon(name="phenomenon", patterns=[pattern])

        decider, subscriber = tc.decider_sub([phenomenon], max_cache=10)

        # First three to complete a run: [1, 2, 3]
        # Next three to halt a run: [1, 2, 4]
        # Last one to generate a run: [1]
        for data in [1, 2, 3, 1, 2, 4, 1]:
            decider.on_receiver_update(event=tc.event_simple(data=data))
            assert decider.update()

        decider.close()
        snap_completed, snap_halted, snap_updated = decider.snapshot()

        # Nothing should have been stored
        assert len(snap_completed) == 0
        assert len(snap_halted) == 0
        assert len(snap_updated) == 0

    def test_snapshot_caching(self):
        pattern = tc.pattern(
            name="pattern",
            data_blocks=[1, 2, 3],
            data_halts=[4])
        phenomenon = tc.phenomenon(name="phenomenon", patterns=[pattern])

        decider, subscriber = tc.decider_sub([phenomenon], max_cache=10)

        # First three to complete a run: [1, 2, 3]
        # Next three to halt a run: [1, 2, 4]
        # Last one to generate a run: [1]
        for data in [1, 2, 3, 1, 2, 4, 1]:
            decider.on_receiver_update(event=tc.event_simple(data=data))
            assert decider.update()

        snap_completed, snap_halted, snap_updated = decider.snapshot()

        # Completed and halted should have been cached
        # Updated should exist in snapshot
        assert len(snap_completed) == 1
        assert len(snap_halted) == 1
        assert len(snap_updated) == 1

    def test_snapshot_not_caching(self):
        pattern = tc.pattern(
            name="pattern",
            data_blocks=[1, 2, 3],
            data_halts=[4])

        phenomenon = tc.phenomenon(name="phenomenon", patterns=[pattern])

        decider, subscriber = tc.decider_sub([phenomenon], max_cache=0)

        # First three to complete a run: [1, 2, 3]
        # Next three to halt a run: [1, 2, 4]
        # Last one to generate a run: [1]
        for data in [1, 2, 3, 1, 2, 4, 1]:
            decider.on_receiver_update(event=tc.event_simple(data=data))
            assert decider.update()

        snap_completed, snap_halted, snap_updated = decider.snapshot()

        # Completed and halted should not have been cached
        # Updated should exist in snapshot
        assert len(snap_completed) == 0
        assert len(snap_halted) == 0
        assert len(snap_updated) == 1

    def test_on_distributed_update_empty_decider_caching(self):
        pattern_name = "pattern"
        phenom_name = "phenom"

        pattern = tc.pattern(
            name=pattern_name,
            data_blocks=[1, 2, 3],
            data_halts=[4])

        phenomenon = tc.phenomenon(name=phenom_name, patterns=[pattern])

        decider, subscriber = tc.decider_sub([phenomenon], max_cache=10)

        completed = [tc.run_tuple(
            run_id="id_completed",
            phenomenon_name=phenom_name,
            pattern_name=pattern_name
        )]
        halted = [tc.run_tuple(
            run_id="id_halted",
            phenomenon_name=phenom_name,
            pattern_name=pattern_name
        )]
        updated = [tc.run_tuple(
            run_id="id_updated",
            phenomenon_name=phenom_name,
            pattern_name=pattern_name
        )]

        decider.on_distributed_update(
            completed=completed,
            halted=halted,
            updated=updated
        )

        snap_completed, snap_halted, snap_updated = decider.snapshot()

        # Completed and halted should have been cached locally
        assert len(snap_completed) == 1
        assert len(snap_halted) == 1

        # Subscriber should have received updates
        assert len(subscriber.completed) == 1
        assert len(subscriber.halted) == 1
        assert len(subscriber.updated) == 1

    def test_on_distributed_update_empty_decider_closed_before_call(self):
        pattern_name = "pattern"
        phenom_name = "phenom"

        pattern = tc.pattern(
            name=pattern_name,
            data_blocks=[1, 2, 3],
            data_halts=[4])
        phenomenon = tc.phenomenon(name=phenom_name, patterns=[pattern])

        decider, subscriber = tc.decider_sub([phenomenon], max_cache=10)

        completed = [tc.run_tuple(
            run_id="id_completed",
            phenomenon_name=phenom_name,
            pattern_name=pattern_name
        )]
        halted = [tc.run_tuple(
            run_id="id_halted",
            phenomenon_name=phenom_name,
            pattern_name=pattern_name
        )]
        updated = [tc.run_tuple(
            run_id="id_updated",
            phenomenon_name=phenom_name,
            pattern_name=pattern_name
        )]

        decider.close()

        decider.on_distributed_update(
            completed=completed,
            halted=halted,
            updated=updated
        )

        snap_completed, snap_halted, snap_updated = decider.snapshot()

        # Nothing should have been cached
        assert len(snap_completed) == 0
        assert len(snap_halted) == 0

        # Nothing should have been sent to the subscriber
        assert len(subscriber.completed) == 0
        assert len(subscriber.halted) == 0
        assert len(subscriber.updated) == 0

    def test_on_distributed_update_empty_decider_not_caching(self):
        pattern_name = "pattern"
        phenom_name = "phenom"

        pattern = tc.pattern(
            name=pattern_name,
            data_blocks=[1, 2, 3],
            data_halts=[4])

        phenomenon = tc.phenomenon(name=phenom_name, patterns=[pattern])

        decider, subscriber = tc.decider_sub([phenomenon], max_cache=0)

        completed = [tc.run_tuple(
            run_id="id_completed",
            phenomenon_name=phenom_name,
            pattern_name=pattern_name
        )]
        halted = [tc.run_tuple(
            run_id="id_halted",
            phenomenon_name=phenom_name,
            pattern_name=pattern_name
        )]
        updated = [tc.run_tuple(
            run_id="id_updated",
            phenomenon_name=phenom_name,
            pattern_name=pattern_name
        )]

        decider.on_distributed_update(
            completed=completed,
            halted=halted,
            updated=updated
        )

        snap_completed, snap_halted, snap_updated = decider.snapshot()

        # Completed and halted should not have been cached locally
        assert len(snap_completed) == 0
        assert len(snap_halted) == 0

        # Check that subscriber has received updates
        assert len(subscriber.completed) == 1
        assert len(subscriber.halted) == 1
        assert len(subscriber.updated) == 1

    def test_on_distributed_update_remove_run_completed_remotely_caching(self):
        pattern_name = "pattern"
        phenom_name = "phenom"

        pattern = tc.pattern(
            name=pattern_name,
            data_blocks=[1, 2, 3],
            data_halts=[4])

        phenomenon = tc.phenomenon(name=phenom_name, patterns=[pattern])

        decider, subscriber = tc.decider_sub([phenomenon], max_cache=10)

        decider.on_receiver_update(tc.event_simple(data=1))
        assert decider.update()

        # Check that subscriber received update
        assert len(subscriber.updated) == 1

        # Only one run should have been generated
        runs = decider.runs_from(phenom_name, pattern_name)
        assert len(runs) == 1

        run = runs[0]

        completed = [tc.run_tuple(
            run_id=run.run_id,
            phenomenon_name=run.phenomenon_name,
            pattern_name=run.pattern.name
        )]

        decider.on_distributed_update(
            completed=completed,
            halted=[],
            updated=[]
        )

        snap_completed, snap_halted, snap_updated = decider.snapshot()

        # Cache should have received completed
        assert len(snap_completed) == 1

        # Subscriber should have received completed
        assert len(subscriber.completed) == 1

    def test_on_distributed_update_remove_run_halted_remotely_caching(self):
        pattern_name = "pattern"
        phenom_name = "phenom"

        pattern = tc.pattern(
            name=pattern_name,
            data_blocks=[1, 2, 3],
            data_halts=[4])

        phenomenon = tc.phenomenon(name=phenom_name, patterns=[pattern])

        decider, subscriber = tc.decider_sub([phenomenon], max_cache=10)

        decider.on_receiver_update(tc.event_simple(data=1))
        assert decider.update()

        # Check that subscriber received update
        assert len(subscriber.updated) == 1

        # Only one run should have been generated
        runs = decider.runs_from(phenom_name, pattern_name)
        assert len(runs) == 1

        run = runs[0]

        halted = [tc.run_tuple(
            run_id=run.run_id,
            phenomenon_name=run.phenomenon_name,
            pattern_name=run.pattern.name
        )]

        decider.on_distributed_update(
            completed=[],
            halted=halted,
            updated=[]
        )

        snap_completed, snap_halted, snap_updated = decider.snapshot()

        # Cache should have received halted
        assert len(snap_halted) == 1

        # Subscriber should have received halted
        assert len(subscriber.halted) == 1

    def test_on_distributed_update_update_existing_run_caching(self):
        pattern_name = "pattern"
        phenom_name = "phenom"

        pattern = tc.pattern(
            name=pattern_name,
            data_blocks=[1, 2, 3],
            data_halts=[4])

        phenomenon = tc.phenomenon(name=phenom_name, patterns=[pattern])

        decider, subscriber = tc.decider_sub([phenomenon], max_cache=10)

        decider.on_receiver_update(tc.event_simple(data=1))
        assert decider.update()

        # Check that subscriber received update
        assert len(subscriber.updated) == 1

        # Only one run should have been generated
        runs = decider.runs_from(phenom_name, pattern_name)
        assert len(runs) == 1

        # Run should be at its first block
        run = runs[0]
        assert run.block_index == 1

        updated = [tc.run_tuple(
            run_id=run.run_id,
            phenomenon_name=run.phenomenon_name,
            pattern_name=run.pattern.name,
            block_index=2
        )]

        decider.on_distributed_update(
            completed=[],
            halted=[],
            updated=updated
        )

        # Check that subscriber has received another update
        assert len(subscriber.updated) == 2

        # Run should have changed block index
        assert run.block_index == 2

    def test_on_distributed_update_nonexistent_pattern_in_updated(self):
        pattern_name = "pattern"
        phenom_name = "phenom"

        pattern = tc.pattern(
            name=pattern_name,
            data_blocks=[1, 2, 3],
            data_halts=[4])

        phenomenon = tc.phenomenon(name=phenom_name, patterns=[pattern])

        decider, subscriber = tc.decider_sub([phenomenon], max_cache=10)

        decider.on_receiver_update(tc.event_simple(data=1))
        assert decider.update()

        # Check that subscriber received update
        assert len(subscriber.updated) == 1

        # Only one run should have been generated
        runs = decider.runs_from(phenom_name, pattern_name)
        assert len(runs) == 1

        # Run should be at its first block
        run = runs[0]
        assert run.block_index == 1

        updated = [tc.run_tuple(
            run_id=run.run_id,
            phenomenon_name=run.phenomenon_name,
            pattern_name="nonexistent_pattern_name",
            block_index=2
        )]

        decider.on_distributed_update(
            completed=[],
            halted=[],
            updated=updated
        )

        # Check that subscriber has not received another update
        assert len(subscriber.updated) == 1

        # Run should not have changed block index
        assert run.block_index == 1

    def test_on_distributed_update_nonexistent_phenomenon_in_updated(self):
        pattern_name = "pattern"
        phenom_name = "phenom"

        pattern = tc.pattern(
            name=pattern_name,
            data_blocks=[1, 2, 3],
            data_halts=[4])

        phenomenon = tc.phenomenon(name=phenom_name, patterns=[pattern])

        decider, subscriber = tc.decider_sub([phenomenon], max_cache=10)

        decider.on_receiver_update(tc.event_simple(data=1))
        assert decider.update()

        # Check that subscriber received update
        assert len(subscriber.updated) == 1

        # Only one run should have been generated
        runs = decider.runs_from(phenom_name, pattern_name)
        assert len(runs) == 1

        # Run should be at its first block
        run = runs[0]
        assert run.block_index == 1

        updated = [tc.run_tuple(
            run_id=run.run_id,
            phenomenon_name="nonexistent_phenomenon_name",
            pattern_name=run.pattern.name,
            block_index=2
        )]

        decider.on_distributed_update(
            completed=[],
            halted=[],
            updated=updated
        )

        # Subscriber should not have received another update
        assert len(subscriber.updated) == 1

        # Run should not have changed block index
        assert run.block_index == 1
