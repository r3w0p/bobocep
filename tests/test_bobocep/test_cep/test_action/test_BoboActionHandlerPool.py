# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from multiprocessing import Manager
from multiprocessing.pool import AsyncResult

import pytest

from bobocep.cep.action.handler import BoboActionHandlerPool, \
    BoboActionHandlerError, _pool_execute_action
from tests.test_bobocep.test_cep.test_action import BoboActionTrue
from tests.test_bobocep.test_cep.test_event import tc_event_complex


class TestValid:

    def test_pool_execute_action(self):
        m = Manager()
        q = m.Queue()

        assert q.qsize() == 0

        _pool_execute_action(
            queue=q,
            action=BoboActionTrue(),
            event=tc_event_complex(),
            max_size=255
        )

        assert q.qsize() == 1

    def test_handle_1_action_1_process(self):
        handler = BoboActionHandlerPool(processes=1, max_size=255)

        assert handler.size() == 0
        result: AsyncResult = handler.handle(
            BoboActionTrue(),
            tc_event_complex())
        result.wait(timeout=5)
        assert handler.size() == 1

    def test_handle_10_actions_1_process(self):
        handler = BoboActionHandlerPool(processes=1, max_size=255)

        assert handler.size() == 0
        for i in range(10):
            handler.handle(BoboActionTrue("action_{}".format(i)),
                           tc_event_complex())
        handler.close()
        handler.join()
        assert handler.size() == 10

    def test_handle_10_actions_3_processes(self):
        handler = BoboActionHandlerPool(processes=3, max_size=255)

        assert handler.size() == 0
        for i in range(10):
            handler.handle(BoboActionTrue("action_{}".format(i)),
                           tc_event_complex())
        handler.close()
        handler.join()
        assert handler.size() == 10

    def test_handle_10_actions_10_processes(self):
        handler = BoboActionHandlerPool(processes=10, max_size=255)

        assert handler.size() == 0
        for i in range(10):
            handler.handle(BoboActionTrue("action_{}".format(i)),
                           tc_event_complex())
        handler.close()
        handler.join()
        assert handler.size() == 10

    def test_get_action_event_empty(self):
        handler = BoboActionHandlerPool(processes=1, max_size=255)

        assert handler.get_handler_response() is None

    def test_get_action_event_not_empty(self):
        handler = BoboActionHandlerPool(processes=1, max_size=255)

        result: AsyncResult = handler.handle(
            BoboActionTrue(), tc_event_complex())
        result.wait(timeout=5)

        assert handler.get_handler_response() is not None

    def test_close(self):
        handler = BoboActionHandlerPool(processes=3, max_size=255)
        assert handler.is_closed() is False

        handler.close()
        assert handler.is_closed() is True


class TestInvalid:

    def test_add_action_event_queue_full(self):
        handler = BoboActionHandlerPool(processes=1, max_size=1)

        result: AsyncResult = handler.handle(
            BoboActionTrue(), tc_event_complex())
        result.wait(timeout=5)

        assert handler.size() == 1

        with pytest.raises(BoboActionHandlerError):
            handler.handle(BoboActionTrue(), tc_event_complex())

    def test_pool_execute_action_queue_full(self):
        m = Manager()
        q = m.Queue(maxsize=1)

        assert q.qsize() == 0

        _pool_execute_action(
            queue=q,
            action=BoboActionTrue(),
            event=tc_event_complex(),
            max_size=1
        )

        assert q.qsize() == 1

        with pytest.raises(BoboActionHandlerError):
            _pool_execute_action(
                queue=q,
                action=BoboActionTrue(),
                event=tc_event_complex(),
                max_size=1
            )
