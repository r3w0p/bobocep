# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""Engine task that generates complex events and triggers actions."""

from queue import Queue
from threading import RLock
from typing import List, Dict

from bobocep.cep.engine.task import BoboEngineTaskError, BoboEngineTask
from bobocep.cep.engine.task.decider import BoboDeciderRunTuple
from bobocep.cep.engine.task.decider.pubsub import BoboDeciderSubscriber
from bobocep.cep.engine.task.producer.pubsub import BoboProducerPublisher
from bobocep.cep.event import BoboEventComplex
from bobocep.cep.gen.event_id import BoboGenEventID
from bobocep.cep.gen.timestamp import BoboGenTimestamp
from bobocep.cep.process import BoboProcess


class BoboProducerError(BoboEngineTaskError):
    """A producer task error."""


class BoboProducer(BoboEngineTask,
                   BoboProducerPublisher,
                   BoboDeciderSubscriber):
    """A producer task."""

    _EXC_PROCESS_NAME_DUP = "duplicate name in processes: {}"
    _EXC_QUEUE_FULL = "queue is full (max size: {})"

    def __init__(self,
                 processes: List[BoboProcess],
                 gen_event_id: BoboGenEventID,
                 gen_timestamp: BoboGenTimestamp,
                 max_size: int = 0):
        super().__init__()
        self._lock: RLock = RLock()
        self._closed: bool = False

        self._processes: Dict[str, BoboProcess] = {}

        for process in processes:
            if process.name not in self._processes:
                self._processes[process.name] = process
            else:
                raise BoboProducerError(
                    self._EXC_PROCESS_NAME_DUP.format(process.name))

        self._gen_event_id: BoboGenEventID = gen_event_id
        self._gen_timestamp: BoboGenTimestamp = gen_timestamp
        self._max_size: int = max(0, max_size)
        self._queue: Queue[BoboDeciderRunTuple] = Queue(self._max_size)

    def update(self) -> bool:
        with self._lock:
            if self._closed:
                return False

            if not self._queue.empty():
                self._handle_completed_run(self._queue.get_nowait())
                return True

            return False

    def close(self) -> None:
        with self._lock:
            self._closed = True

    def is_closed(self) -> bool:
        with self._lock:
            return self._closed

    def _handle_completed_run(self, run_state: BoboDeciderRunTuple) -> None:
        if run_state.process_name not in self._processes:
            raise BoboProducerError(run_state.process_name)

        process: BoboProcess = self._processes[run_state.process_name]

        if not any(run_state.pattern_name == pattern.name
                   for pattern in process.patterns):
            raise BoboProducerError(run_state.pattern_name)

        event_complex = BoboEventComplex(
            event_id=self._gen_event_id.generate(),
            timestamp=self._gen_timestamp.generate(),
            data=process.datagen(process, run_state.history)
            if process.datagen is not None else None,
            process_name=run_state.process_name,
            pattern_name=run_state.pattern_name,
            history=run_state.history)

        for subscriber in self._subscribers:
            subscriber.on_producer_update(event_complex)

    def on_decider_update(self,
                          halted_complete: List[BoboDeciderRunTuple],
                          halted_incomplete: List[BoboDeciderRunTuple],
                          updated: List[BoboDeciderRunTuple]) -> None:
        with self._lock:
            if self._closed:
                return

            for run in halted_complete:
                if not self._queue.full():
                    self._queue.put(run)
                else:
                    raise BoboProducerError(
                        self._EXC_QUEUE_FULL.format(self._max_size))

    def size(self) -> int:
        with self._lock:
            return self._queue.qsize()
