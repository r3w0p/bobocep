# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from queue import Queue

from bobocep.action.bobo_action import BoboAction
from bobocep.action.bobo_action_response import BoboActionResponse
from bobocep.action.handler.bobo_action_handler import \
    BoboActionHandler
from bobocep.action.handler.bobo_action_handler_error import \
    BoboActionHandlerError
from bobocep.event.bobo_event_complex import BoboEventComplex


class BoboActionHandlerBlocking(BoboActionHandler):

    def __init__(self,
                 name: str,
                 max_size: int):
        super().__init__(name, max_size)

        self._queue: "Queue[BoboActionResponse]" = Queue(self._max_size)

    def _execute_action(self,
                        action: BoboAction,
                        event: BoboEventComplex) -> None:
        self._add_response(action.execute(event))

    def _get_queue(self) -> Queue:
        return self._queue

    def _add_response(self, response: BoboActionResponse) -> None:
        with self._lock:
            if not self._queue.full():
                self._queue.put(response)
            else:
                raise BoboActionHandlerError(
                    self._EXC_QUEUE_FULL.format(self._max_size))
