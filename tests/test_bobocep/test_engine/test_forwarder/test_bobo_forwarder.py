# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

import tests.common as tc
from bobocep.action.handler.bobo_action_handler_blocking import \
    BoboActionHandlerBlocking
from bobocep.action.handler.bobo_action_handler_pool import \
    BoboActionHandlerPool
from bobocep.engine.forwarder.bobo_forwarder import BoboForwarder
from bobocep.engine.forwarder.bobo_forwarder_error import BoboForwarderError
from bobocep.event.event_id.bobo_event_id_unique import BoboEventIDUnique
from bobocep.process.bobo_process import BoboProcess


class TestValid:

    def test_process_complex_event_blocking(self):
        event = tc.event_complex()
        process = tc.process(datagen=lambda p, h: True,
                             action=tc.BoboActionTrue())

        forwarder, subscriber = tc.forwarder_sub([process], max_size=255)
        assert len(subscriber.output) == 0

        forwarder.on_producer_complex_event(event)
        forwarder.update()
        assert len(subscriber.output) == 1

    def test_process_complex_event_pool(self):
        event = tc.event_complex()
        process = tc.process(datagen=lambda p, h: True,
                             action=tc.BoboActionTrue())

        forwarder, subscriber = tc.forwarder_sub(
            processes=[process],
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

    def test_close_then_update(self):
        forwarder, subscriber = tc.forwarder_sub([tc.process()])

        forwarder.close()
        assert forwarder.is_closed()
        assert forwarder.update() is False

    def test_close_then_on_producer_complex_event(self):
        forwarder, subscriber = tc.forwarder_sub([tc.process()])

        forwarder.close()
        assert forwarder.is_closed()
        assert forwarder.size() == 0

        forwarder.on_producer_complex_event(tc.event_complex())
        assert forwarder.size() == 0


class TestInvalid:

    def test_add_on_queue_full(self):
        forwarder, subscriber = tc.forwarder_sub([tc.process()], max_size=1)

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