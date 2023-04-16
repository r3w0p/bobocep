# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

from bobocep.cep.engine.decider.runserial import BoboRunSerial
from bobocep.cep.engine.producer.producer import BoboProducerError, \
    BoboProducer
from bobocep.cep.event import BoboHistory
from bobocep.cep.gen.event_id import BoboGenEventIDUnique
from bobocep.cep.gen.timestamp import BoboGenTimestampEpoch
from tests.test_bobocep.test_cep.test_action import BoboActionTrue
from tests.test_bobocep.test_cep.test_engine.test_producer import \
    tc_producer_sub
from tests.test_bobocep.test_cep.test_event import tc_event_simple
from tests.test_bobocep.test_cep.test_phenom import tc_phenomenon


class TestValid:

    def test_produce_complex_event_on_run(self):
        phenom = tc_phenomenon(
            name="phenom",
            datagen=lambda p, h: True,
            action=BoboActionTrue())

        producer, subscriber = tc_producer_sub([phenom])

        history = BoboHistory(events={"pattern_group": [tc_event_simple()]})

        producer.on_decider_update(
            completed=[BoboRunSerial(
                run_id="run_id",
                phenomenon_name="phenom",
                pattern_name="pattern",
                block_index=3,
                history=history
            )],
            halted=[],
            updated=[],
            local=True
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
        producer, subscriber = tc_producer_sub([tc_phenomenon()])
        assert producer.size() == 0

        history = BoboHistory(events={"pattern_group": [tc_event_simple()]})

        producer.on_decider_update(
            completed=[BoboRunSerial(
                run_id="run_id",
                phenomenon_name="phenom",
                pattern_name="pattern",
                block_index=3,
                history=history
            )],
            halted=[],
            updated=[],
            local=True
        )

        assert producer.size() == 1

    def test_close_then_update(self):
        producer, subscriber = tc_producer_sub([tc_phenomenon()])

        producer.close()
        assert producer.is_closed()
        assert producer.update() is False

    def test_close_then_on_decider_update_1_complete(self):
        producer, subscriber = tc_producer_sub([tc_phenomenon()])

        producer.close()
        assert producer.is_closed()
        assert producer.size() == 0

        history = BoboHistory(events={"pattern_group": [tc_event_simple()]})

        producer.on_decider_update(
            completed=[BoboRunSerial(
                run_id="run_id",
                phenomenon_name="phenom",
                pattern_name="pattern",
                block_index=3,
                history=history
            )],
            halted=[],
            updated=[],
            local=True
        )

        assert producer.size() == 0


class TestInvalid:

    def test_add_run_on_queue_full(self):
        phenom_1 = tc_phenomenon("phenom_1")
        phenom_2 = tc_phenomenon("phenom_2")
        producer, subscriber = tc_producer_sub(
            [phenom_1, phenom_2], max_size=1)

        history = BoboHistory(events={"pattern_group": [tc_event_simple()]})

        producer.on_decider_update(
            completed=[BoboRunSerial(
                run_id="run_id",
                phenomenon_name="phenom_1",
                pattern_name="pattern",
                block_index=3,
                history=history
            )],
            halted=[],
            updated=[],
            local=True
        )

        with pytest.raises(BoboProducerError):
            producer.on_decider_update(
                completed=[BoboRunSerial(
                    run_id="run_id",
                    phenomenon_name="phenom_2",
                    pattern_name="pattern",
                    block_index=3,
                    history=history
                )],
                halted=[],
                updated=[],
                local=True
            )

    def test_duplicate_phenomena_names(self):
        with pytest.raises(BoboProducerError):
            BoboProducer(
                phenomena=[tc_phenomenon(), tc_phenomenon()],
                gen_event_id=BoboGenEventIDUnique(),
                gen_timestamp=BoboGenTimestampEpoch(),
                max_size=255)

    def test_decider_run_phenomenon_does_not_exist(self):
        producer, subscriber = tc_producer_sub([tc_phenomenon()], max_size=255)

        history = BoboHistory(events={"pattern_group": [tc_event_simple()]})

        producer.on_decider_update(
            completed=[BoboRunSerial(
                run_id="run_id",
                phenomenon_name="phenom_invalid",
                pattern_name="pattern",
                block_index=3,
                history=history
            )],
            halted=[],
            updated=[],
            local=True
        )

        with pytest.raises(BoboProducerError):
            producer.update()

    def test_decider_run_pattern_does_not_exist(self):
        producer, subscriber = tc_producer_sub([tc_phenomenon()], max_size=255)

        history = BoboHistory(events={"pattern_group": [tc_event_simple()]})

        producer.on_decider_update(
            completed=[BoboRunSerial(
                run_id="run_id",
                phenomenon_name="phenom_invalid",
                pattern_name="pattern",
                block_index=3,
                history=history
            )],
            halted=[],
            updated=[],
            local=True
        )

        with pytest.raises(BoboProducerError):
            producer.update()
