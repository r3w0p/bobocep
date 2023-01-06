# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from queue import Queue
from threading import RLock
from typing import Dict, List, Optional

from bobocep.cep.action.handler.bobo_action_handler import BoboActionHandler
from bobocep.cep.engine.bobo_engine_task import BoboEngineTask
from bobocep.cep.engine.forwarder.bobo_forwarder_error import \
    BoboForwarderError
from bobocep.cep.engine.forwarder.bobo_forwarder_publisher import \
    BoboForwarderPublisher
from bobocep.cep.engine.producer.bobo_producer_subscriber import \
    BoboProducerSubscriber
from bobocep.cep.event.bobo_event_action import BoboEventAction
from bobocep.cep.event.bobo_event_complex import BoboEventComplex
from bobocep.cep.gen.event_id.bobo_gen_event_id import BoboGenEventID
from bobocep.cep.process.bobo_process import BoboProcess


class BoboForwarder(BoboEngineTask,
                    BoboForwarderPublisher,
                    BoboProducerSubscriber):
    """A forwarder task."""

    _EXC_PROCESS_NAME_DUP = "duplicate name in processes: {}"
    _EXC_QUEUE_FULL = "queue is full (max size: {})"

    def __init__(self,
                 processes: List[BoboProcess],
                 handler: BoboActionHandler,
                 gen_event_id: BoboGenEventID,
                 max_size: int = 0):
        super().__init__()

        self._lock: RLock = RLock()
        self._closed: bool = False

        self._processes: Dict[str, BoboProcess] = {}

        for process in processes:
            if process.name not in self._processes:
                self._processes[process.name] = process
            else:
                raise BoboForwarderError(
                    self._EXC_PROCESS_NAME_DUP.format(process.name))

        self._handler: BoboActionHandler = handler
        self._gen_event_id: BoboGenEventID = gen_event_id
        self._max_size: int = max(0, max_size)
        self._queue: Queue[BoboEventComplex] = Queue(self._max_size)

    def update(self) -> bool:
        with self._lock:
            if self._closed:
                return False

            handle = self._update_handler()
            response = self._update_responses()
            return handle or response

    def close(self) -> None:
        with self._lock:
            self._closed = True

    def is_closed(self) -> bool:
        with self._lock:
            return self._closed

    def _update_handler(self) -> bool:
        if not self._queue.empty():
            event: BoboEventComplex = self._queue.get_nowait()

            if event.process_name in self._processes:
                process: BoboProcess = self._processes[event.process_name]

                if process.action is not None:
                    self._handler.handle(action=process.action, event=event)
            return True
        return False

    def _update_responses(self) -> bool:
        event: Optional[BoboEventAction] = \
            self._handler.get_action_event()

        if event is not None:
            for subscriber in self._subscribers:
                subscriber.on_forwarder_update(event)
            return True
        return False

    def on_producer_update(self, event: BoboEventComplex) -> None:
        with self._lock:
            if self._closed:
                return

            if not self._queue.full():
                self._queue.put(event)
            else:
                raise BoboForwarderError(
                    self._EXC_QUEUE_FULL.format(self._max_size))

    def size(self) -> int:
        with self._lock:
            return self._queue.qsize()
