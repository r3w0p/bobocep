# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from typing import List

import pytest

import tests.common as tc
from bobocep.action.handler.bobo_action_handler import BoboActionHandler
from bobocep.action.handler.bobo_action_handler_blocking import \
    BoboActionHandlerBlocking
from bobocep.action.handler.bobo_action_handler_pool import \
    BoboActionHandlerPool
from bobocep.engine.forwarder.bobo_forwarder import BoboForwarder
from bobocep.engine.forwarder.bobo_forwarder_error import BoboForwarderError
from bobocep.engine.forwarder.bobo_forwarder_subscriber import \
    BoboForwarderSubscriber
from bobocep.event.bobo_event_action import BoboEventAction
from bobocep.event.event_id.bobo_event_id import BoboEventID
from bobocep.event.event_id.bobo_event_id_unique import BoboEventIDUnique
from bobocep.process.bobo_process import BoboProcess
from bobocep.process.pattern.bobo_pattern import BoboPattern


class StubForwarderSubscriber(BoboForwarderSubscriber):

    def __init__(self):
        super().__init__()
        self.output: List[BoboEventAction] = []

    def on_forwarder_action_event(self, event: BoboEventAction):
        self.output.append(event)


def _forsub(patterns: List[BoboPattern],
            handler: BoboActionHandler = None,
            event_id_gen: BoboEventID = None,
            max_size: int = 255):
    process = BoboProcess(name="process",
                          datagen=lambda p, h: True,
                          patterns=patterns,
                          action=tc.BoboActionTrue(name="action_true"))

    forwarder = BoboForwarder(
        processes=[process],
        handler=handler if handler is not None else
        BoboActionHandlerBlocking(max_size=max_size),
        event_id_gen=event_id_gen if event_id_gen is not None else
        BoboEventIDUnique(),
        max_size=max_size)

    subscriber = StubForwarderSubscriber()
    forwarder.subscribe(subscriber=subscriber)

    return forwarder, subscriber


class TestValid:

    def test_process_complex_event_blocking(self):
        pattern = tc.pattern()
        event = tc.event_complex()

        forwarder, subscriber = _forsub([pattern], max_size=255)
        assert len(subscriber.output) == 0

        forwarder.on_producer_complex_event(event)
        forwarder.update()
        assert len(subscriber.output) == 1

    def test_process_complex_event_pool(self):
        pattern = tc.pattern()
        event = tc.event_complex()

        forwarder, subscriber = _forsub(
            patterns=[pattern],
            handler=BoboActionHandlerPool(
                max_size=255,
                processes=1),
            max_size=255)
        assert len(subscriber.output) == 0

        forwarder.on_producer_complex_event(event)
        forwarder.update()

        forwarder.handler.close()
        forwarder.handler.join()
        forwarder.update()
        assert len(subscriber.output) == 1


class TestInvalid:

    def test_add_on_queue_full(self):
        forwarder, subscriber = _forsub([tc.pattern()], max_size=1)

        forwarder.on_producer_complex_event(tc.event_complex())

        with pytest.raises(BoboForwarderError):
            forwarder.on_producer_complex_event(tc.event_complex())

    def test_duplicate_process_names(self):
        process_1 = BoboProcess(
            name="process",
            datagen=lambda p, h: True,
            patterns=[tc.pattern()],
            action=None)

        process_2 = BoboProcess(
            name="process",
            datagen=lambda p, h: True,
            patterns=[tc.pattern()],
            action=None)

        with pytest.raises(BoboForwarderError):
            BoboForwarder(
                processes=[process_1, process_2],
                handler=BoboActionHandlerBlocking(max_size=255),
                event_id_gen=BoboEventIDUnique(),
                max_size=255)
