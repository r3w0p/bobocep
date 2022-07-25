# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from multiprocessing import Manager, Pool
from queue import Queue

from bobocep.action.bobo_action import BoboAction
from bobocep.action.bobo_action_response import BoboActionResponse
from bobocep.action.handler.bobo_action_handler import \
    BoboActionHandler
from bobocep.event.bobo_event_complex import BoboEventComplex


def _pool_execute_action(
        queue: Queue,
        action: BoboAction,
        event: BoboEventComplex):
    queue.put(action.execute(event))


class BoboActionHandlerPool(BoboActionHandler):

    def __init__(self,
                 name: str,
                 max_size: int,
                 processes: int):
        super().__init__(name, max_size)

        self._processes = processes
        self._pool = Pool(processes=processes)
        self._manager = Manager()
        self._queue: "Queue[BoboActionResponse]" = self._manager.Queue()

    def _execute_action(self,
                        action: BoboAction,
                        event: BoboEventComplex) -> None:
        self._pool.starmap(_pool_execute_action,
                           [(self._queue, action, event)])

    def _get_queue(self) -> Queue:
        return self._queue

    def close(self) -> None:
        with self._lock:
            self._pool.close()

    def join(self) -> None:
        with self._lock:
            self._pool.join()
