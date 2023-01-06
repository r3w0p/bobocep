# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from multiprocessing import Manager, Pool
from multiprocessing.pool import AsyncResult
from queue import Queue

from bobocep.cep.action.bobo_action import BoboAction
from bobocep.cep.action.handler.bobo_action_handler import \
    BoboActionHandler
from bobocep.cep.action.handler.bobo_action_handler_error import \
    BoboActionHandlerError
from bobocep.cep.event.bobo_event_action import BoboEventAction
from bobocep.cep.event.bobo_event_complex import BoboEventComplex


def _pool_execute_action(
        queue: Queue,
        action: BoboAction,
        event: BoboEventComplex):
    queue.put(action.execute(event))


class BoboActionHandlerPool(BoboActionHandler):
    """An action handler that uses multiprocessing for action execution."""

    def __init__(self, processes: int, max_size: int = 0):
        super().__init__(max_size)

        self._processes = processes
        self._pool = Pool(processes=processes)
        self._manager = Manager()
        self._queue: "Queue[BoboEventAction]" = self._manager.Queue()

    def _execute_action(self,
                        action: BoboAction,
                        event: BoboEventComplex) -> AsyncResult:
        # The queue size is checked manually before action execution because
        # a 'queue full' error within a running process would not be visible
        # outside of the process itself. Also, a 'maxsize' parameter for the
        # Manager queue does not appear to work correctly e.g. a max_size of 1
        # causes unit tests to 'hang'.
        if self._queue.qsize() >= self._max_size:
            raise BoboActionHandlerError(
                self._EXC_QUEUE_FULL.format(self._max_size))

        return self._pool.starmap_async(
            _pool_execute_action, [(self._queue, action, event)])

    def _get_queue(self) -> Queue:
        return self._queue

    def close(self) -> None:
        with self._lock:
            self._pool.close()

    def join(self) -> None:
        with self._lock:
            self._pool.join()
