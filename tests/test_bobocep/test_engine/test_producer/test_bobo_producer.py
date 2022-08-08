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
from bobocep.process.pattern.bobo_pattern import BoboPattern


def _decpro(patterns: List[BoboPattern],
            event_id_gen: BoboEventID = None,
            max_size: int = 255):
    producer = BoboProducer(
        processes=[tc.process(patterns=patterns)],
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

    def test_on_decider_completed_run(self):
        producer, subscriber = _decpro([tc.pattern()])

        assert producer.size() == 0

        producer.on_decider_completed_run(
            process_name="process",
            pattern_name="pattern",
            history=BoboHistory(events={}))

        assert producer.size() == 1

    def test_on_forwarder_action_response(self):
        """"""  # todo


class TestInvalid:

    def test_add_run_on_queue_full(self):
        producer, subscriber = _decpro([tc.pattern()], max_size=1)
        assert True  # todo

    def test_add_response_on_queue_full(self):
        producer, subscriber = _decpro([tc.pattern()], max_size=1)
        assert True  # todo

    def test_duplicate_process_names(self):
        with pytest.raises(BoboProducerError):
            BoboProducer(
                processes=[tc.process(patterns=[tc.pattern()]),
                           tc.process(patterns=[tc.pattern()])],
                event_id_gen=BoboEventIDUnique(),
                max_size=255)
