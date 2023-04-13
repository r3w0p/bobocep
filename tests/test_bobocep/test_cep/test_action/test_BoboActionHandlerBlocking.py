# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

from bobocep.cep.action.handler import BoboActionHandlerBlocking, \
    BoboActionHandlerError
from tests.test_bobocep.test_cep.test_action import BoboActionTrue
from tests.test_bobocep.test_cep.test_event import tc_event_complex


class TestValid:

    def test_handle_action(self):
        handler = BoboActionHandlerBlocking(max_size=255)

        assert handler.size() == 0
        handler.handle(BoboActionTrue(), tc_event_complex())
        assert handler.size() == 1

    def test_get_action_event_empty(self):
        handler = BoboActionHandlerBlocking(max_size=255)

        assert handler.get_handler_response() is None

    def test_get_action_event_not_empty(self):
        handler = BoboActionHandlerBlocking(max_size=255)

        handler.handle(BoboActionTrue(), tc_event_complex())
        assert handler.get_handler_response() is not None

    def test_close(self):
        handler = BoboActionHandlerBlocking(max_size=255)
        assert handler.is_closed() is False

        handler.close()
        assert handler.is_closed() is True


class TestInvalid:

    def test_add_action_event_queue_full(self):
        handler = BoboActionHandlerBlocking(max_size=1)
        handler.handle(BoboActionTrue(), tc_event_complex())

        with pytest.raises(BoboActionHandlerError):
            handler.handle(BoboActionTrue(), tc_event_complex())
