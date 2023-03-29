# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from typing import Optional, List

from bobocep.cep.action.handler import BoboActionHandler, \
    BoboActionHandlerBlocking
from bobocep.cep.engine.forwarder.forwarder import BoboForwarder
from bobocep.cep.engine.forwarder.pubsub import BoboForwarderSubscriber
from bobocep.cep.event import BoboEventAction
from bobocep.cep.gen.event_id import BoboGenEventID, BoboGenEventIDUnique
from bobocep.cep.phenomenon.phenomenon import BoboPhenomenon


class StubForwarderSubscriber(BoboForwarderSubscriber):

    def __init__(self):
        super().__init__()
        self.output: List[BoboEventAction] = []

    def on_forwarder_update(self, event: BoboEventAction):
        self.output.append(event)


def tc_forwarder_sub(
        phenomena: List[BoboPhenomenon],
        handler: Optional[BoboActionHandler] = None,
        event_id_gen: Optional[BoboGenEventID] = None,
        max_size: int = 255):
    forwarder = BoboForwarder(
        phenomena=phenomena,
        handler=handler if handler is not None else
        BoboActionHandlerBlocking(max_size=max_size),
        gen_event_id=event_id_gen if event_id_gen is not None else
        BoboGenEventIDUnique(),
        max_size=max_size)

    subscriber = StubForwarderSubscriber()
    forwarder.subscribe(subscriber=subscriber)

    return forwarder, subscriber
