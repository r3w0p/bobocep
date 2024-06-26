# Copyright (c) 2019-2024 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Handlers that coordinate the execution of actions.
"""

import logging
from abc import ABC, abstractmethod
from queue import Queue
from threading import RLock
from typing import Any, Optional, Tuple, NamedTuple

from bobocep import BoboError
from bobocep.cep.action.action import BoboAction
from bobocep.cep.event import BoboEventComplex

_EXC_QUEUE_FULL = "queue is full (max size: {})"


class BoboActionHandlerError(BoboError):
    """
    An action handler error.
    """


class BoboHandlerResponse(NamedTuple):
    """
    A handler response to action execution.
    """
    action_name: str
    complex_event: BoboEventComplex
    success: bool
    data: Any


class BoboActionHandler(ABC):
    """
    An abstract action handler.
    """

    def __init__(self, max_size: int = 0):
        """
        :param max_size: Maximum queue size.
            Default: 0 (unbounded).
        """
        super().__init__()
        self._closed: bool = False
        self._lock: RLock = RLock()
        self._max_size = max(0, max_size)

    def handle(self,
               action: BoboAction,
               event: BoboEventComplex) -> Any:
        """
        Handle an action.

        :param action: The action to handle.
        :param event: The complex event that caused the action to trigger.

        :return: A return value from handling the action.
        """
        with self._lock:
            return self._execute_action(action, event)

    def is_closed(self) -> bool:
        """
        :return: `True` if handler is closed; `False` otherwise.
        """
        with self._lock:
            return self._closed

    def close(self) -> None:
        """
        Close the handler.
        """
        with self._lock:
            try:
                self._on_closing()
            finally:
                self._closed = True

    @abstractmethod
    def _on_closing(self) -> None:
        """
        Close the handler.
        """

    @abstractmethod
    def _execute_action(
            self,
            action: BoboAction,
            event: BoboEventComplex) -> Any:
        """
        Execute an action.

        :param action: The action to execute.
        :param event: The complex event that caused the action to trigger.

        :return: A return value from executing the action.
        """

    @abstractmethod
    def _get_queue(self) -> Queue:
        """
        :return: The handler queue.
        """

    def get_handler_response(self) -> Optional[BoboHandlerResponse]:
        """
        :return: Action response from queue, or `None` if queue is empty.
        """
        with self._lock:
            queue = self._get_queue()
            if not queue.empty():
                return queue.get_nowait()
            return None

    def size(self) -> int:
        """
        :return: The size of the handler queue.
        """
        with self._lock:
            return self._get_queue().qsize()


class BoboActionHandlerBlocking(BoboActionHandler):
    """
    An action handler that blocks during action execution.
    """

    def __init__(self, max_size: int = 0):
        """
        :param max_size: Maximum queue size.
            Default: 0 (unbounded).
        """
        super().__init__(max_size)

        self._queue: "Queue[BoboHandlerResponse]" = Queue(self._max_size)

    def _execute_action(self,
                        action: BoboAction,
                        event: BoboEventComplex) -> None:
        """
        :param action: Action to execute.
        :param event: Complex event associated with the action.
        """
        action_ret: Tuple[bool, Any] = action.execute(event)

        hres = BoboHandlerResponse(
            action_name=action.name,
            complex_event=event,
            success=action_ret[0],
            data=action_ret[1]
        )

        if not self._queue.full():
            self._queue.put(hres)
        else:
            raise BoboActionHandlerError(
                _EXC_QUEUE_FULL.format(self._max_size))

    def _on_closing(self) -> None:
        """
        Action on closing the handler.
        """
        pass

    def _get_queue(self) -> Queue:
        """
        :return: Handler queue.
        """
        return self._queue


def _pool_execute_action(
        queue: Queue,
        action: BoboAction,
        event: BoboEventComplex,
        max_size: int
) -> None:
    """
    :param queue: A queue in which to put the action response that is
        returned after execution.
    :param action: The action to execute.
    :param event: The complex event that triggered the action being executed.
    :param max_size: Maximum queue size.
    """
    try:
        action_ret: Tuple[bool, Any] = action.execute(event)

    except (Exception,) as e:
        logging.error(e)
        raise e

    hres = BoboHandlerResponse(
        action_name=action.name,
        complex_event=event,
        success=action_ret[0],
        data=action_ret[1]
    )

    if not queue.full():
        queue.put(hres)
    else:
        raise BoboActionHandlerError(
            _EXC_QUEUE_FULL.format(max_size))


class BoboActionHandlerMultithreading(BoboActionHandler):
    """
    An action handler that uses multithreading for action execution.
    """
    from multiprocessing.pool import AsyncResult

    def __init__(self, threads: int, max_size: int = 0):
        """
        :param threads: Number of thread processes to use
            for handling actions.
        :param max_size: Maximum queue size.
            Default: 0 (unbounded).
        """
        from multiprocessing.pool import ThreadPool
        super().__init__(max_size)

        self._threads = threads
        self._pool: ThreadPool = ThreadPool(processes=threads)
        self._queue: Queue[BoboHandlerResponse] = Queue()

    def join(self) -> None:
        """
        Join the multiprocessing pool.
        """
        with self._lock:
            self._pool.join()

    def _execute_action(self,
                        action: BoboAction,
                        event: BoboEventComplex) -> AsyncResult:
        """
        :param action: Action to execute.
        :param event: Complex event associated with the action.

        :return: Result from asynchronous action execution.
        """
        # The queue size is checked manually because queue.full() does not
        # seem to work properly...
        if self._max_size > 0 and (self._queue.qsize() >= self._max_size):
            raise BoboActionHandlerError(
                _EXC_QUEUE_FULL.format(self._max_size))

        return self._pool.starmap_async(
            _pool_execute_action, [
                (self._queue, action, event, self._max_size)
            ])

    def _get_queue(self) -> Queue:
        """
        :return: Handler queue.
        """
        return self._queue

    def _on_closing(self) -> None:
        """
        Action on closing the handler.
        """
        self._pool.close()


class BoboActionHandlerMultiprocessing(BoboActionHandler):
    """
    An action handler that uses multiprocessing for action execution.
    """
    from multiprocessing.pool import AsyncResult

    def __init__(self, processes: int, max_size: int = 0):
        """
        :param processes: Number of multicore processes to use
            for handling actions.
        :param max_size: Maximum queue size.
            Default: 0 (unbounded).
        """
        from multiprocessing import Manager, Pool
        super().__init__(max_size)

        self._processes = processes
        self._pool = Pool(processes=processes)
        self._manager = Manager()
        self._queue: "Queue[BoboHandlerResponse]" = self._manager.Queue()

    def join(self) -> None:
        """
        Join the multiprocessing pool.
        """
        with self._lock:
            self._pool.join()

    def _execute_action(self,
                        action: BoboAction,
                        event: BoboEventComplex) -> AsyncResult:
        """
        :param action: Action to execute.
        :param event: Complex event associated with the action.

        :return: Result from asynchronous action execution.
        """
        # The queue size is checked manually before action execution because
        # a 'queue full' error within a running process would not be visible
        # outside of the process itself. Also, a 'maxsize' parameter for the
        # Manager queue does not appear to work correctly e.g. a max_size of 1
        # causes unit tests to 'hang'.
        if self._max_size > 0 and (self._queue.qsize() >= self._max_size):
            raise BoboActionHandlerError(
                _EXC_QUEUE_FULL.format(self._max_size))

        return self._pool.starmap_async(
            _pool_execute_action, [
                (self._queue, action, event, self._max_size)
            ])

    def _get_queue(self) -> Queue:
        """
        :return: Handler queue.
        """
        return self._queue

    def _on_closing(self) -> None:
        """
        Action on closing the handler.
        """
        self._pool.close()
