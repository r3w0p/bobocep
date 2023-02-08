# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

import tests.common as tc
from bobocep.cep.action.handler import BoboActionHandlerPool, \
    BoboActionHandlerBlocking
from bobocep.cep.engine.task.forwarder import BoboForwarderError, BoboForwarder
from bobocep.cep.gen.event_id import BoboGenEventIDUnique
from bobocep.cep.phenomenon import BoboPhenomenon


class TestValid:

    def test_phenomenon_complex_event_blocking(self):
        event = tc.event_complex()
        phenom = tc.phenomenon(datagen=lambda p, h: True,
                                action=tc.BoboActionTrue())

        forwarder, subscriber = tc.forwarder_sub([phenom], max_size=255)
        assert len(subscriber.output) == 0

        forwarder.on_producer_update(event)
        forwarder.update()
        assert len(subscriber.output) == 1

    def test_phenomenon_complex_event_pool(self):
        event = tc.event_complex()
        phenom = tc.phenomenon(datagen=lambda p, h: True,
                               action=tc.BoboActionTrue())

        forwarder, subscriber = tc.forwarder_sub(
            phenomena=[phenom],
            handler=BoboActionHandlerPool(processes=1, max_size=255),
            max_size=255)
        assert len(subscriber.output) == 0

        forwarder.on_producer_update(event)
        forwarder.update()

        forwarder._handler.close()
        forwarder._handler.join()
        forwarder.update()
        assert len(subscriber.output) == 1

    def test_close_then_update(self):
        forwarder, subscriber = tc.forwarder_sub([tc.phenomenon()])

        forwarder.close()
        assert forwarder.is_closed()
        assert forwarder.update() is False

    def test_close_then_on_producer_update(self):
        forwarder, subscriber = tc.forwarder_sub([tc.phenomenon()])

        forwarder.close()
        assert forwarder.is_closed()
        assert forwarder.size() == 0

        forwarder.on_producer_update(tc.event_complex())
        assert forwarder.size() == 0


class TestInvalid:

    def test_add_on_queue_full(self):
        forwarder, subscriber = tc.forwarder_sub([tc.phenomenon()], max_size=1)

        forwarder.on_producer_update(tc.event_complex())

        with pytest.raises(BoboForwarderError):
            forwarder.on_producer_update(tc.event_complex())

    def test_duplicate_phenomena_names(self):
        phenom_1 = BoboPhenomenon(
            name="phenom",
            datagen=lambda p, h: True,
            patterns=[tc.pattern()],
            action=None)

        phenom_2 = BoboPhenomenon(
            name="phenom",
            datagen=lambda p, h: True,
            patterns=[tc.pattern()],
            action=None)

        with pytest.raises(BoboForwarderError):
            BoboForwarder(
                phenomena=[phenom_1, phenom_2],
                handler=BoboActionHandlerBlocking(max_size=255),
                gen_event_id=BoboGenEventIDUnique(),
                max_size=255)
