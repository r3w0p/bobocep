# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC, abstractmethod
from queue import Queue
from threading import RLock
from typing import Union, Any

from bobocep.action.bobo_action import BoboAction
from bobocep.event.bobo_event_action import BoboEventAction
from bobocep.event.bobo_event_complex import BoboEventComplex


class BoboActionHandler(ABC):
    _EXC_QUEUE_FULL = "queue is full (max size: {0})"

    def __init__(self, max_size: int):
        super().__init__()

        self._max_size = max_size
        self._lock = RLock()

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

    def get_response(self) -> Union[BoboEventAction, None]:
        with self._lock:
            queue = self._get_queue()
            if not queue.empty():
                return queue.get_nowait()
            return None

    def size(self) -> int:
        with self._lock:
            return self._get_queue().qsize()
