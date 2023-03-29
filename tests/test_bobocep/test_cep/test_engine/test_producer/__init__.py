# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from typing import Optional, List

from bobocep.cep.engine.producer.producer import BoboProducer
from bobocep.cep.engine.producer.pubsub import BoboProducerSubscriber
from bobocep.cep.event import BoboEventComplex
from bobocep.cep.gen.event_id import BoboGenEventID, BoboGenEventIDUnique
from bobocep.cep.gen.timestamp import BoboGenTimestampEpoch
from bobocep.cep.phenomenon.phenomenon import BoboPhenomenon


class StubProducerSubscriber(BoboProducerSubscriber):

    def __init__(self):
        super().__init__()
        self.output: List[BoboEventComplex] = []

    def on_producer_update(self, event: BoboEventComplex):
        self.output.append(event)


def tc_producer_sub(
        phenomena: List[BoboPhenomenon],
        event_id_gen: Optional[BoboGenEventID] = None,
        max_size: int = 255):
    producer = BoboProducer(
        phenomena=phenomena,
        gen_event_id=event_id_gen if event_id_gen is not None else
        BoboGenEventIDUnique(),
        gen_timestamp=BoboGenTimestampEpoch(),
        max_size=max_size)

    subscriber = StubProducerSubscriber()
    producer.subscribe(subscriber=subscriber)

    return producer, subscriber
