# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC, abstractmethod
from queue import Queue
from threading import RLock
from typing import Union

from bobocep.action.bobo_action import BoboAction
from bobocep.action.bobo_action_response import BoboActionResponse
from bobocep.action.handler.bobo_action_handler_error import \
    BoboActionHandlerError
from bobocep.event.bobo_event_complex import BoboEventComplex


class BoboActionHandler(ABC):
    _EXC_NAME_LEN = "'name' must have a length greater than 0"
    _EXC_QUEUE_FULL = "queue is full (max size: {0})"

    def __init__(self, name: str, max_size: int):
        super().__init__()

        if len(name) == 0:
            raise BoboActionHandlerError(self._EXC_NAME_LEN)

        self._name = name
        self._max_size = max_size
        self._lock = RLock()

    def handle(self,
               action: BoboAction,
               event: BoboEventComplex) -> None:
        with self._lock:
            self._execute_action(action, event)

    @abstractmethod
    def _execute_action(self,
                        action: BoboAction,
                        event: BoboEventComplex) -> None:
        """"""

    @abstractmethod
    def _get_queue(self) -> Queue:
        """"""

    def get_response(self) -> Union[BoboActionResponse, None]:
        with self._lock:
            queue = self._get_queue()
            if not queue.empty():
                return queue.get_nowait()
            return None

    def size(self) -> int:
        with self._lock:
            return self._get_queue().qsize()
