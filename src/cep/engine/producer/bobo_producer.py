# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from datetime import datetime
from queue import Queue
from threading import RLock
from typing import Dict, List

from src.cep.engine.bobo_engine_task import BoboEngineTask
from src.cep.engine.decider.bobo_decider_run_tuple import BoboDeciderRunTuple
from src.cep.engine.decider.bobo_decider_subscriber import \
    BoboDeciderSubscriber
from src.cep.engine.producer.bobo_producer_error import BoboProducerError
from src.cep.engine.producer.bobo_producer_publisher import \
    BoboProducerPublisher
from src.cep.event.bobo_event_complex import BoboEventComplex
from src.cep.event.event_id_gen.bobo_event_id_gen import BoboEventIDGen
from src.cep.event.timestamp_gen.bobo_timestamp_gen_epoch import \
    BoboTimestampGenEpoch
from src.cep.process.bobo_process import BoboProcess


class BoboProducer(BoboEngineTask,
                   BoboProducerPublisher,
                   BoboDeciderSubscriber):
    """A producer task."""

    _EXC_PROCESS_NAME_DUP = "duplicate name in processes: {0}"
    _EXC_QUEUE_FULL = "queue is full (max size: {0})"

    def __init__(self,
                 processes: List[BoboProcess],
                 event_id_gen: BoboEventIDGen,
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
            timestamp=BoboTimestampGenEpoch.generate(),
            data=process.datagen(process, runtup.history),
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
