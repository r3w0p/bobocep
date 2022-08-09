# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

import tests.common as tc
from bobocep.action.handler.bobo_action_handler_blocking import \
    BoboActionHandlerBlocking
from bobocep.action.handler.bobo_action_handler_error import \
    BoboActionHandlerError


class TestValid:

    def test_handle_action(self):
        handler = BoboActionHandlerBlocking(max_size=255)

        assert handler.size() == 0
        handler.handle(tc.BoboActionTrue(), tc.event_complex())
        assert handler.size() == 1

    def test_get_action_event_empty(self):
        handler = BoboActionHandlerBlocking(max_size=255)

        assert handler.get_action_event() is None

    def test_get_action_event_not_empty(self):
        handler = BoboActionHandlerBlocking(max_size=255)

        handler.handle(tc.BoboActionTrue(), tc.event_complex())
        assert handler.get_action_event() is not None


class TestInvalid:

    def test_add_action_event_queue_full(self):
        handler = BoboActionHandlerBlocking(max_size=1)
        handler.handle(tc.BoboActionTrue(), tc.event_complex())

        with pytest.raises(BoboActionHandlerError):
            handler.handle(tc.BoboActionTrue(), tc.event_complex())
