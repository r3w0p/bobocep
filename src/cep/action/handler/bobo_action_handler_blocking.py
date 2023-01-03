# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from queue import Queue

from src.cep.action.bobo_action import BoboAction
from src.cep.action.handler.bobo_action_handler import \
    BoboActionHandler
from src.cep.action.handler.bobo_action_handler_error import \
    BoboActionHandlerError
from src.cep.event.bobo_event_action import BoboEventAction
from src.cep.event.bobo_event_complex import BoboEventComplex


class BoboActionHandlerBlocking(BoboActionHandler):
    """An action handler that executes without multithreading or
    multiprocessing."""

    def __init__(self, max_size: int):
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