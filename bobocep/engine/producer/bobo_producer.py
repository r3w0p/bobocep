# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from queue import Queue
from threading import RLock
from typing import List, Dict

from bobocep.engine.bobo_engine_task import BoboEngineTask
from bobocep.engine.decider.bobo_decider_run import BoboDeciderRun
from bobocep.engine.decider.bobo_decider_subscriber import \
    BoboDeciderSubscriber
from bobocep.exception.bobo_key_error import BoboKeyError
from bobocep.exception.bobo_queue_full_error import BoboQueueFullError
from bobocep.process.bobo_process import BoboProcess


class BoboProducer(BoboEngineTask, BoboDeciderSubscriber):
    _EXC_PROCESS_NAME_DUP = "duplicate name in processes: {}"
    _EXC_QUEUE_FULL = "queue is full (max size: {})"

    def __init__(self,
                 processes: List[BoboProcess],
                 max_size: int):
        super().__init__()

        self._processes: Dict[str, BoboProcess] = {}

        for process in processes:
            if process.name not in self._processes:
                self._processes[process.name] = process
            else:
                raise BoboKeyError(
                    self._EXC_PROCESS_NAME_DUP.format(process.name))

        self._max_size = max_size
        self._queue: Queue = Queue(maxsize=self._max_size)
        self._lock = RLock()

    def update(self) -> None:
        with self._lock:
            if not self._queue.empty():
                pass

    def on_decider_completed_run(self, run: BoboDeciderRun):
        with self._lock:
            if not self._queue.full():
                self._queue.put(run)
            else:
                raise BoboQueueFullError(
                    self._EXC_QUEUE_FULL.format(self._max_size))
