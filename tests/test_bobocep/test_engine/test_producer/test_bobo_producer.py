# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from typing import List

import pytest

import tests.common as tc
from bobocep.engine.producer.bobo_producer import BoboProducer
from bobocep.engine.producer.bobo_producer_error import BoboProducerError
from bobocep.engine.producer.bobo_producer_subscriber import \
    BoboProducerSubscriber
from bobocep.event.bobo_event_complex import BoboEventComplex
from bobocep.event.bobo_history import BoboHistory
from bobocep.event.event_id.bobo_event_id import BoboEventID
from bobocep.event.event_id.bobo_event_id_unique import BoboEventIDUnique
from bobocep.process.bobo_process import BoboProcess


def _prosub(processes: List[BoboProcess],
            event_id_gen: BoboEventID = None,
            max_size: int = 255):
    producer = BoboProducer(
        processes=processes,
        event_id_gen=event_id_gen if event_id_gen is not None else
        BoboEventIDUnique(),
        max_size=max_size)

    subscriber = StubProducerSubscriber()
    producer.subscribe(subscriber=subscriber)

    return producer, subscriber


class StubProducerSubscriber(BoboProducerSubscriber):

    def __init__(self):
        super().__init__()
        self.events = []

    def on_producer_complex_event(self, event: BoboEventComplex):
        self.events.append(event)


class TestValid:

    def test_produce_complex_event_on_run(self):
        process = tc.process(
            name="process",
            data=True,
            patterns=[tc.pattern(name="pattern")],
            action=tc.BoboActionTrue(name="action_true"))

        producer, subscriber = _prosub([process])

        history = BoboHistory(events={})
        producer.on_decider_completed_run(
            process_name="process",
            pattern_name="pattern",
            history=history)
        assert producer.size() == 1

        producer.update()
        assert producer.size() == 0
        assert len(subscriber.events) == 1

        assert subscriber.events[0].data is True
        assert subscriber.events[0].process_name == "process"
        assert subscriber.events[0].pattern_name == "pattern"
        assert subscriber.events[0].history == history

    def test_on_decider_completed_run(self):
        producer, subscriber = _prosub([tc.process()])
        assert producer.size() == 0

        producer.on_decider_completed_run(
            process_name="process",
            pattern_name="pattern",
            history=BoboHistory(events={}))

        assert producer.size() == 1


class TestInvalid:

    def test_add_run_on_queue_full(self):
        process_1 = tc.process("process_1")
        process_2 = tc.process("process_2")
        producer, subscriber = _prosub([process_1, process_2], max_size=1)

        producer.on_decider_completed_run(
            process_name="process_1",
            pattern_name="pattern",
            history=BoboHistory(events={}))

        with pytest.raises(BoboProducerError):
            producer.on_decider_completed_run(
                process_name="process_2",
                pattern_name="pattern",
                history=BoboHistory(events={}))

    def test_duplicate_process_names(self):
        with pytest.raises(BoboProducerError):
            BoboProducer(
                processes=[tc.process(), tc.process()],
                event_id_gen=BoboEventIDUnique(),
                max_size=255)

    def test_decider_run_process_does_not_exist(self):
        producer, subscriber = _prosub([tc.process()], max_size=255)

        producer.on_decider_completed_run(
            process_name="process_invalid",
            pattern_name="pattern",
            history=BoboHistory(events={}))

        with pytest.raises(BoboProducerError):
            producer.update()

    def test_decider_run_pattern_does_not_exist(self):
        producer, subscriber = _prosub([tc.process()], max_size=255)

        producer.on_decider_completed_run(
            process_name="process",
            pattern_name="pattern_invalid",
            history=BoboHistory(events={}))

        with pytest.raises(BoboProducerError):
            producer.update()
