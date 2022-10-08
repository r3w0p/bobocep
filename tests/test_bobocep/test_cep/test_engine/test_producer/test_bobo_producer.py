# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

import tests.common as tc
from bobocep.cep.engine.decider.bobo_decider_run import BoboDeciderRunTuple
from bobocep.cep.engine.producer.bobo_producer import BoboProducer
from bobocep.cep.engine.producer.bobo_producer_error import BoboProducerError
from bobocep.cep.event.bobo_history import BoboHistory
from bobocep.cep.event.event_id_gen.bobo_event_id_gen_unique import \
    BoboEventIDGenUnique


class TestValid:

    def test_produce_complex_event_on_run(self):
        process = tc.process(
            datagen=lambda p, h: True,
            action=tc.BoboActionTrue())

        producer, subscriber = tc.producer_sub([process])

        history = BoboHistory(events={})

        producer.on_decider_run_changes(
            halted_complete=[BoboDeciderRunTuple(
                process_name="process",
                pattern_name="pattern",
                history=history
            )],
            halted_incomplete=[],
            updated=[]
        )

        assert producer.size() == 1

        producer.update()
        assert producer.size() == 0
        assert len(subscriber.output) == 1

        assert subscriber.output[0].data is True
        assert subscriber.output[0].process_name == "process"
        assert subscriber.output[0].pattern_name == "pattern"
        assert subscriber.output[0].history == history

    def test_on_decider_run_changes_1_complete(self):
        producer, subscriber = tc.producer_sub([tc.process()])
        assert producer.size() == 0

        producer.on_decider_run_changes(
            halted_complete=[BoboDeciderRunTuple(
                process_name="process",
                pattern_name="pattern",
                history=BoboHistory(events={})
            )],
            halted_incomplete=[],
            updated=[]
        )

        assert producer.size() == 1

    def test_close_then_update(self):
        producer, subscriber = tc.producer_sub([tc.process()])

        producer.close()
        assert producer.is_closed()
        assert producer.update() is False

    def test_close_then_on_decider_run_changes_1_complete(self):
        producer, subscriber = tc.producer_sub([tc.process()])

        producer.close()
        assert producer.is_closed()
        assert producer.size() == 0

        producer.on_decider_run_changes(
            halted_complete=[BoboDeciderRunTuple(
                process_name="process",
                pattern_name="pattern",
                history=BoboHistory(events={})
            )],
            halted_incomplete=[],
            updated=[]
        )

        assert producer.size() == 0


class TestInvalid:

    def test_add_run_on_queue_full(self):
        process_1 = tc.process("process_1")
        process_2 = tc.process("process_2")
        producer, subscriber = tc.producer_sub(
            [process_1, process_2], max_size=1)

        producer.on_decider_run_changes(
            halted_complete=[BoboDeciderRunTuple(
                process_name="process_1",
                pattern_name="pattern",
                history=BoboHistory(events={})
            )],
            halted_incomplete=[],
            updated=[]
        )

        with pytest.raises(BoboProducerError):
            producer.on_decider_run_changes(
                halted_complete=[BoboDeciderRunTuple(
                    process_name="process_2",
                    pattern_name="pattern",
                    history=BoboHistory(events={})
                )],
                halted_incomplete=[],
                updated=[]
            )

    def test_duplicate_process_names(self):
        with pytest.raises(BoboProducerError):
            BoboProducer(
                processes=[tc.process(), tc.process()],
                event_id_gen=BoboEventIDGenUnique(),
                max_size=255)

    def test_decider_run_process_does_not_exist(self):
        producer, subscriber = tc.producer_sub([tc.process()], max_size=255)

        producer.on_decider_run_changes(
            halted_complete=[BoboDeciderRunTuple(
                process_name="process_invalid",
                pattern_name="pattern",
                history=BoboHistory(events={})
            )],
            halted_incomplete=[],
            updated=[]
        )

        with pytest.raises(BoboProducerError):
            producer.update()

    def test_decider_run_pattern_does_not_exist(self):
        producer, subscriber = tc.producer_sub([tc.process()], max_size=255)

        producer.on_decider_run_changes(
            halted_complete=[BoboDeciderRunTuple(
                process_name="process",
                pattern_name="pattern_invalid",
                history=BoboHistory(events={})
            )],
            halted_incomplete=[],
            updated=[]
        )

        with pytest.raises(BoboProducerError):
            producer.update()
