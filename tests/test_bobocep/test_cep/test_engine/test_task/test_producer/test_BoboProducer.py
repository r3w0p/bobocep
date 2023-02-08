# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

import tests.common as tc
from bobocep.cep.engine.task.decider import BoboRunTuple
from bobocep.cep.engine.task.producer import BoboProducerError, BoboProducer
from bobocep.cep.event import BoboHistory
from bobocep.cep.gen.event_id import BoboGenEventIDUnique
from bobocep.cep.gen.timestamp import BoboGenTimestampEpoch


class TestValid:

    def test_produce_complex_event_on_run(self):
        phenom = tc.phenomenon(
            name="phenom",
            datagen=lambda p, h: True,
            action=tc.BoboActionTrue())

        producer, subscriber = tc.producer_sub([phenom])

        history = BoboHistory(events={})

        producer.on_decider_update(
            completed=[BoboRunTuple(
                run_id="run_id",
                phenomenon_name="phenom",
                pattern_name="pattern",
                block_index=3,
                history=history
            )],
            halted=[],
            updated=[]
        )

        assert producer.size() == 1

        producer.update()
        assert producer.size() == 0
        assert len(subscriber.output) == 1

        assert subscriber.output[0].data is True
        assert subscriber.output[0].phenomenon_name == "phenom"
        assert subscriber.output[0].pattern_name == "pattern"
        assert subscriber.output[0].history == history

    def test_on_decider_update_1_complete(self):
        producer, subscriber = tc.producer_sub([tc.phenomenon()])
        assert producer.size() == 0

        producer.on_decider_update(
            completed=[BoboRunTuple(
                run_id="run_id",
                phenomenon_name="phenom",
                pattern_name="pattern",
                block_index=3,
                history=BoboHistory({})
            )],
            halted=[],
            updated=[]
        )

        assert producer.size() == 1

    def test_close_then_update(self):
        producer, subscriber = tc.producer_sub([tc.phenomenon()])

        producer.close()
        assert producer.is_closed()
        assert producer.update() is False

    def test_close_then_on_decider_update_1_complete(self):
        producer, subscriber = tc.producer_sub([tc.phenomenon()])

        producer.close()
        assert producer.is_closed()
        assert producer.size() == 0

        producer.on_decider_update(
            completed=[BoboRunTuple(
                run_id="run_id",
                phenomenon_name="phenom",
                pattern_name="pattern",
                block_index=3,
                history=BoboHistory({})
            )],
            halted=[],
            updated=[]
        )

        assert producer.size() == 0


class TestInvalid:

    def test_add_run_on_queue_full(self):
        phenom_1 = tc.phenomenon("phenom_1")
        phenom_2 = tc.phenomenon("phenom_2")
        producer, subscriber = tc.producer_sub(
            [phenom_1, phenom_2], max_size=1)

        producer.on_decider_update(
            completed=[BoboRunTuple(
                run_id="run_id",
                phenomenon_name="phenom_1",
                pattern_name="pattern",
                block_index=3,
                history=BoboHistory({})
            )],
            halted=[],
            updated=[]
        )

        with pytest.raises(BoboProducerError):
            producer.on_decider_update(
                completed=[BoboRunTuple(
                    run_id="run_id",
                    phenomenon_name="phenom_2",
                    pattern_name="pattern",
                    block_index=3,
                    history=BoboHistory({})
                )],
                halted=[],
                updated=[]
            )

    def test_duplicate_phenomena_names(self):
        with pytest.raises(BoboProducerError):
            BoboProducer(
                phenomena=[tc.phenomenon(), tc.phenomenon()],
                gen_event_id=BoboGenEventIDUnique(),
                gen_timestamp=BoboGenTimestampEpoch(),
                max_size=255)

    def test_decider_run_phenomenon_does_not_exist(self):
        producer, subscriber = tc.producer_sub([tc.phenomenon()], max_size=255)

        producer.on_decider_update(
            completed=[BoboRunTuple(
                run_id="run_id",
                phenomenon_name="phenom_invalid",
                pattern_name="pattern",
                block_index=3,
                history=BoboHistory({})
            )],
            halted=[],
            updated=[]
        )

        with pytest.raises(BoboProducerError):
            producer.update()

    def test_decider_run_pattern_does_not_exist(self):
        producer, subscriber = tc.producer_sub([tc.phenomenon()], max_size=255)

        producer.on_decider_update(
            completed=[BoboRunTuple(
                run_id="run_id",
                phenomenon_name="phenom_invalid",
                pattern_name="pattern",
                block_index=3,
                history=BoboHistory({})
            )],
            halted=[],
            updated=[]
        )

        with pytest.raises(BoboProducerError):
            producer.update()
