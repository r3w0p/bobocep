# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from queue import Queue
from threading import RLock
from typing import Dict, List, Union

from bobocep.action.handler.bobo_action_handler import BoboActionHandler
from bobocep.engine.bobo_engine_task import BoboEngineTask
from bobocep.engine.forwarder.bobo_forwarder_error import BoboForwarderError
from bobocep.engine.forwarder.bobo_forwarder_publisher import \
    BoboForwarderPublisher
from bobocep.event.bobo_event_action import BoboEventAction
from bobocep.event.bobo_event_complex import BoboEventComplex
from bobocep.event.event_id.bobo_event_id import BoboEventID
from bobocep.process.bobo_process import BoboProcess


class BoboForwarder(BoboEngineTask, BoboForwarderPublisher):
    _EXC_PROCESS_NAME_DUP = "duplicate name in processes: {0}"
    _EXC_QUEUE_FULL = "queue is full (max size: {0})"

    def __init__(self,
                 processes: List[BoboProcess],
                 handler: BoboActionHandler,
                 event_id_gen: BoboEventID,
                 max_size: int):
        super().__init__()

        self._processes: Dict[str, BoboProcess] = {}

        for process in processes:
            if process.name not in self._processes:
                self._processes[process.name] = process
            else:
                raise BoboForwarderError(
                    self._EXC_PROCESS_NAME_DUP.format(process.name))

        self.handler: BoboActionHandler = handler
        self._event_id_gen: BoboEventID = event_id_gen
        self._max_size: int = max_size
        self._queue: Queue[BoboEventComplex] = Queue(self._max_size)
        self._lock: RLock = RLock()

    def update(self) -> None:
        with self._lock:
            self._update_handler()
            self._update_responses()

    def _update_handler(self):
        if not self._queue.empty():
            event: BoboEventComplex = self._queue.get_nowait()

            if event.process_name in self._processes:
                process: BoboProcess = self._processes[event.process_name]

                if process.action is not None:
                    self.handler.handle(action=process.action, event=event)

    def _update_responses(self):
        response: Union[BoboEventAction, None] = \
            self.handler.get_response()

        if response is not None:
            for subscriber in self._subscribers:
                subscriber.on_forwarder_action_response(response)

    def on_producer_complex_event(self, event: BoboEventComplex):
        with self._lock:
            if not self._queue.full():
                self._queue.put(event)
            else:
                raise BoboForwarderError(
                    self._EXC_QUEUE_FULL.format(self._max_size))
