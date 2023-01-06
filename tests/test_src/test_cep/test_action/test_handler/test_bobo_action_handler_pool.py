# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from multiprocessing import Manager
from multiprocessing.pool import AsyncResult
from queue import Queue

import pytest

import tests.common as tc
from bobocep.cep.action.handler.bobo_action_handler_error import \
    BoboActionHandlerError
from bobocep.cep.action.handler.bobo_action_handler_pool import \
    BoboActionHandlerPool
from bobocep.cep.action.handler.bobo_action_handler_pool import \
    _pool_execute_action
from bobocep.cep.event.bobo_event_action import BoboEventAction


class TestValid:

    def test_pool_execute_action(self):
        m = Manager()
        q: "Queue[BoboEventAction]" = m.Queue()

        assert q.qsize() == 0

        _pool_execute_action(
            queue=q,
            action=tc.BoboActionTrue(),
            event=tc.event_complex())

        assert q.qsize() == 1

    def test_handle_1_action_1_process(self):
        handler = BoboActionHandlerPool(processes=1, max_size=255)

        assert handler.size() == 0
        result: AsyncResult = handler.handle(
            tc.BoboActionTrue(),
            tc.event_complex())
        result.wait(timeout=5)
        assert handler.size() == 1

    def test_handle_10_actions_1_process(self):
        handler = BoboActionHandlerPool(processes=1, max_size=255)

        assert handler.size() == 0
        for i in range(10):
            handler.handle(tc.BoboActionTrue("action_{}".format(i)),
                           tc.event_complex())
        handler.close()
        handler.join()
        assert handler.size() == 10

    def test_handle_10_actions_3_processes(self):
        handler = BoboActionHandlerPool(processes=3, max_size=255)

        assert handler.size() == 0
        for i in range(10):
            handler.handle(tc.BoboActionTrue("action_{}".format(i)),
                           tc.event_complex())
        handler.close()
        handler.join()
        assert handler.size() == 10

    def test_handle_10_actions_10_processes(self):
        handler = BoboActionHandlerPool(processes=10, max_size=255)

        assert handler.size() == 0
        for i in range(10):
            handler.handle(tc.BoboActionTrue("action_{}".format(i)),
                           tc.event_complex())
        handler.close()
        handler.join()
        assert handler.size() == 10

    def test_get_action_event_empty(self):
        handler = BoboActionHandlerPool(processes=1, max_size=255)

        assert handler.get_action_event() is None

    def test_get_action_event_not_empty(self):
        handler = BoboActionHandlerPool(processes=1, max_size=255)

        result: AsyncResult = handler.handle(
            tc.BoboActionTrue(), tc.event_complex())
        result.wait(timeout=5)

        assert handler.get_action_event() is not None


class TestInvalid:

    def test_add_action_event_queue_full(self):
        handler = BoboActionHandlerPool(processes=1, max_size=1)

        result: AsyncResult = handler.handle(
            tc.BoboActionTrue(), tc.event_complex())
        result.wait(timeout=5)

        assert handler.size() == 1

        with pytest.raises(BoboActionHandlerError):
            handler.handle(tc.BoboActionTrue(), tc.event_complex())
