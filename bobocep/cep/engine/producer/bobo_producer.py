# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from queue import Queue
from threading import RLock
from typing import Dict, List

from bobocep.cep.engine.bobo_engine_task import BoboEngineTask
from bobocep.cep.engine.decider.bobo_decider_run_tuple import BoboDeciderRunTuple
from bobocep.cep.engine.decider.bobo_decider_subscriber import \
    BoboDeciderSubscriber
from bobocep.cep.engine.producer.bobo_producer_error import BoboProducerError
from bobocep.cep.engine.producer.bobo_producer_publisher import \
    BoboProducerPublisher
from bobocep.cep.event.bobo_event_complex import BoboEventComplex
from bobocep.cep.gen.event_id.bobo_gen_event_id import BoboGenEventID
from bobocep.cep.gen.timestamp.bobo_gen_timestamp_epoch import \
    BoboGenTimestampEpoch
from bobocep.cep.process.bobo_process import BoboProcess


class BoboProducer(BoboEngineTask,
                   BoboProducerPublisher,
                   BoboDeciderSubscriber):
    """A producer task."""

    _EXC_PROCESS_NAME_DUP = "duplicate name in processes: {0}"
    _EXC_QUEUE_FULL = "queue is full (max size: {0})"

    def __init__(self,
                 processes: List[BoboProcess],
                 event_id_gen: BoboGenEventID,
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
        self._timegen = BoboGenTimestampEpoch()
        self._max_size = max_size
        self._queue: Queue[BoboDeciderRunTuple] = Queue(self._max_size)
        self._closed = False

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

    def _handle_completed_run(self, runtup: BoboDeciderRunTuple):
        if runtup.process_name not in self._processes:
            raise BoboProducerError(runtup.process_name)

        process = self._processes[runtup.process_name]

        if not any(runtup.pattern_name == pattern.name
                   for pattern in process.patterns):
            raise BoboProducerError(runtup.pattern_name)

        event_complex = BoboEventComplex(
            event_id=self._event_id_gen.generate(),
            timestamp=self._timegen.generate(),
            data=process.datagen(process, runtup.history)
            if process.datagen is not None else None,
            process_name=runtup.process_name,
            pattern_name=runtup.pattern_name,
            history=runtup.history)

        for subscriber in self._subscribers:
            subscriber.on_producer_update(event_complex)

    def on_decider_update(self,
                          halted_complete: List[BoboDeciderRunTuple],
                          halted_incomplete: List[BoboDeciderRunTuple],
                          updated: List[BoboDeciderRunTuple]):
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
