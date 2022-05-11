# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from datetime import datetime
from queue import Queue
from threading import RLock
from typing import Dict, List, Tuple

from bobocep.action.bobo_action_handler import BoboActionHandler
from bobocep.engine.bobo_engine_task import BoboEngineTask
from bobocep.engine.decider.bobo_decider_run import BoboDeciderRun
from bobocep.engine.decider.bobo_decider_subscriber import \
    BoboDeciderSubscriber
from bobocep.engine.producer.bobo_producer_publisher import \
    BoboProducerPublisher
from bobocep.event.bobo_event_complex import BoboEventComplex
from bobocep.event.bobo_history import BoboHistory
from bobocep.event.event_id.bobo_event_id import BoboEventID
from bobocep.exception.bobo_key_error import BoboKeyError
from bobocep.exception.bobo_pattern_not_found_error import \
    BoboPatternNotFoundError
from bobocep.exception.bobo_process_not_found_error import \
    BoboProcessNotFoundError
from bobocep.exception.bobo_queue_full_error import BoboQueueFullError
from bobocep.process.bobo_process import BoboProcess


class BoboProducer(BoboEngineTask,
                   BoboProducerPublisher,
                   BoboDeciderSubscriber):
    _EXC_PROCESS_NAME_DUP = "duplicate name in processes: {0}"
    _EXC_HANDLER_NAME_DUP = "duplicate name in handlers: {0}"
    _EXC_QUEUE_FULL = "queue is full (max size: {0})"

    def __init__(self,
                 processes: List[BoboProcess],
                 handlers: List[BoboActionHandler],
                 event_id_gen: BoboEventID,
                 max_size: int):
        super().__init__()

        self._processes: Dict[str, BoboProcess] = {}

        for process in processes:
            if process.name not in self._processes:
                self._processes[process.name] = process
            else:
                raise BoboKeyError(
                    self._EXC_PROCESS_NAME_DUP.format(process.name))

        self._handlers: Dict[str, BoboActionHandler] = {}

        for handler in handlers:
            if handler.name not in self._handlers:
                self._handlers[handler.name] = handler
            else:
                raise BoboKeyError(
                    self._EXC_HANDLER_NAME_DUP.format(handler.name))

        # todo subscribe each handler to producer
        # todo queue for action events

        self._event_id_gen = event_id_gen
        self._max_size = max_size
        self._queue: Queue[Tuple[str, str, BoboHistory]] = \
            Queue(self._max_size)
        self._lock = RLock()

    def update(self) -> None:
        with self._lock:
            if not self._queue.empty():
                process_name, pattern_name, history = self._queue.get_nowait()

                if process_name not in self._processes:
                    raise BoboProcessNotFoundError(process_name)

                process = self._processes[process_name]

                if not any(pattern_name == pattern.name
                           for pattern in process.patterns):
                    raise BoboPatternNotFoundError(pattern_name)

                event_complex = BoboEventComplex(
                    event_id=self._event_id_gen.generate(),
                    timestamp=datetime.now(),
                    data=process.datagen(process, history),
                    process_name=process_name,
                    pattern_name=pattern_name,
                    history=history)

                for subscriber in self._subscribers:
                    subscriber.on_producer_complex_event(event_complex)

                for request in process.requests:
                    if request.handler_name in self._handlers:
                        self._handlers[request.handler_name].handle(request)
                    else:
                        pass  # todo raise exception

    def on_decider_completed_run(self,
                                 process_name: str,
                                 pattern_name: str,
                                 history: BoboHistory):
        with self._lock:
            if not self._queue.full():
                self._queue.put((process_name, pattern_name, history))
            else:
                raise BoboQueueFullError(
                    self._EXC_QUEUE_FULL.format(self._max_size))
