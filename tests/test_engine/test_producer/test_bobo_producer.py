# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from typing import List

from bobocep.engine.producer.bobo_producer import BoboProducer
from bobocep.engine.producer.bobo_producer_subscriber import BoboProducerSubscriber
from bobocep.event.bobo_event_complex import BoboEventComplex
from bobocep.event.bobo_history import BoboHistory
from bobocep.event.event_id.bobo_event_id import BoboEventID
from bobocep.event.event_id.bobo_event_id_unique import BoboEventIDUnique
from bobocep.process.pattern.bobo_pattern import BoboPattern
from bobocep.process.pattern.bobo_pattern_block import BoboPatternBlock
from bobocep.process.pattern.predicate.bobo_predicate_call import \
    BoboPredicateCall
from bobocep.process.bobo_process import BoboProcess


def _decpro(patterns: List[BoboPattern],
            event_id_gen: BoboEventID = None,
            max_size: int = 255):

    process = BoboProcess(name="process", datagen=lambda p, h: True, patterns=patterns, action=None)

    producer = BoboProducer(
        processes=[process],
        event_id_gen=event_id_gen if event_id_gen is not None else BoboEventIDUnique(),
        max_size=max_size)

    subscriber = StubProducerSubscriber()
    producer.subscribe(subscriber=subscriber)

    return producer, subscriber


def _pattern_minimum(name: str = "pattern", group: str = "group"):
    return BoboPattern(
        name=name,
        blocks=[BoboPatternBlock(
            group=group,
            predicates=[BoboPredicateCall(call=lambda e, h: None)],
            strict=False,
            loop=False,
            negated=False,
            optional=False)],
        preconditions=[BoboPredicateCall(call=lambda e, h: None)],
        haltconditions=[BoboPredicateCall(call=lambda e, h: None)])


class StubProducerSubscriber(BoboProducerSubscriber):

    def __init__(self):
        super().__init__()
        self.events = []

    def on_producer_complex_event(self, event: BoboEventComplex):
        self.events.append(event)


class TestValid:

    def test_on_decider_completed_run(self):
        producer, subscriber = _decpro([_pattern_minimum()])

        assert producer.size() == 0

        producer.on_decider_completed_run(
            process_name="process_1",
            pattern_name="pattern_1",
            history=BoboHistory(events={}))

        assert producer.size() == 1

    def test_on_forwarder_action_response(self):
        """"""  # todo
