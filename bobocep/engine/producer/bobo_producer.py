# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from datetime import datetime
from queue import Queue
from threading import RLock
from typing import Dict, List, Tuple

from bobocep.engine.bobo_engine_task import BoboEngineTask
from bobocep.engine.decider.bobo_decider_subscriber import \
    BoboDeciderSubscriber
from bobocep.engine.producer.bobo_producer_error import BoboProducerError
from bobocep.engine.producer.bobo_producer_publisher import \
    BoboProducerPublisher
from bobocep.event.bobo_event_complex import BoboEventComplex
from bobocep.event.bobo_history import BoboHistory
from bobocep.event.event_id.bobo_event_id import BoboEventID
from bobocep.process.bobo_process import BoboProcess


class BoboProducer(BoboEngineTask,
                   BoboProducerPublisher,
                   BoboDeciderSubscriber):
    """A producer task."""

    _EXC_PROCESS_NAME_DUP = "duplicate name in processes: {0}"
    _EXC_QUEUE_FULL = "queue is full (max size: {0})"

    def __init__(self,
                 processes: List[BoboProcess],
                 event_id_gen: BoboEventID,
                 max_size: int):
        super().__init__()
        self._lock: RLock = RLock()

        self._processes: Dict[str, BoboProcess] = {}

        for process in processes:
            if process.name not in self._processes:
                self._processes[process.name] = process
            else:
                raise BoboProducerError(
                    self._EXC_PROCESS_NAME_DUP.format(process.name))

        self._event_id_gen = event_id_gen
        self._max_size = max_size
        self._queue: Queue[Tuple[str, str, BoboHistory]] = \
            Queue(self._max_size)
        self._closed = False

    def update(self) -> bool:
        with self._lock:
            if self._closed:
                return False

            if not self._queue.empty():
                data: Tuple[str, str, BoboHistory] = self._queue.get_nowait()

                process_name, pattern_name, history = data
                self._handle_completed_run(
                    process_name, pattern_name, history)
                return True

            return False

    def close(self) -> None:
        with self._lock:
            self._closed = True

    def is_closed(self) -> bool:
        with self._lock:
            return self._closed

    def _handle_completed_run(self, process_name, pattern_name, history):
        if process_name not in self._processes:
            raise BoboProducerError(process_name)

        process = self._processes[process_name]

        if not any(pattern_name == pattern.name
                   for pattern in process.patterns):
            raise BoboProducerError(pattern_name)

        event_complex = BoboEventComplex(
            event_id=self._event_id_gen.generate(),
            timestamp=datetime.now(),
            data=process.datagen(process, history),
            process_name=process_name,
            pattern_name=pattern_name,
            history=history)

        for subscriber in self._subscribers:
            subscriber.on_producer_complex_event(event_complex)

    def on_decider_completed_run(self,
                                 process_name: str,
                                 pattern_name: str,
                                 history: BoboHistory):
        with self._lock:
            if self._closed:
                return

            if not self._queue.full():
                self._queue.put((process_name, pattern_name, history))
            else:
                raise BoboProducerError(
                    self._EXC_QUEUE_FULL.format(self._max_size))

    def size(self) -> int:
        with self._lock:
            return self._queue.qsize()
