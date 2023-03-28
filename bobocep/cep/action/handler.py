# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Handlers that coordinate the execution of actions.
"""

from abc import ABC, abstractmethod
from multiprocessing import Manager, Pool
from multiprocessing.pool import AsyncResult
from queue import Queue
from threading import RLock
from typing import Any, Optional

from bobocep import BoboError
from bobocep.cep.action.action import BoboAction
from bobocep.cep.event import BoboEventAction, BoboEventComplex


class BoboActionHandlerError(BoboError):
    """
    An action handler error.
    """


class BoboActionHandler(ABC):
    """
    A handler for the execution of actions.
    """

    _EXC_QUEUE_FULL = "queue is full (max size: {})"

    def __init__(self, max_size: int = 0):
        super().__init__()
        self._lock: RLock = RLock()
        self._max_size = max(0, max_size)

    def handle(self,
               action: BoboAction,
               event: BoboEventComplex) -> Any:
        with self._lock:
            return self._execute_action(action, event)

    @abstractmethod
    def _execute_action(self,
                        action: BoboAction,
                        event: BoboEventComplex) -> Any:
        """"""

    @abstractmethod
    def _get_queue(self) -> Queue:
        """"""

    def get_action_event(self) -> Optional[BoboEventAction]:
        with self._lock:
            queue = self._get_queue()
            if not queue.empty():
                return queue.get_nowait()
            return None

    def size(self) -> int:
        with self._lock:
            return self._get_queue().qsize()


class BoboActionHandlerBlocking(BoboActionHandler):
    """
    An action handler that executes without multithreading or multiprocessing.
    """

    def __init__(self, max_size: int = 0):
        super().__init__(max_size)

        self._queue: "Queue[BoboEventAction]" = Queue(self._max_size)

    def _execute_action(self,
                        action: BoboAction,
                        event: BoboEventComplex) -> None:
        self._add_action_event(action.execute(event))

    def _get_queue(self) -> Queue:
        return self._queue

    def _add_action_event(self, event: BoboEventAction) -> None:
        with self._lock:
            if not self._queue.full():
                self._queue.put(event)
            else:
                raise BoboActionHandlerError(
                    self._EXC_QUEUE_FULL.format(self._max_size))


def _pool_execute_action(
        queue: Queue,
        action: BoboAction,
        event: BoboEventComplex):
    queue.put(action.execute(event))


class BoboActionHandlerPool(BoboActionHandler):
    """
    An action handler that uses multiprocessing for action execution.
    """

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
