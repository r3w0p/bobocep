# Copyright (c) The BoboCEP Authors
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from queue import Queue, Full
from threading import RLock

from bobocep.engine.bobo_engine_task import BoboEngineTask
from bobocep.engine.decider.bobo_decider_run import BoboDeciderRun
from bobocep.engine.decider.bobo_decider_subscriber import \
    BoboDeciderSubscriber
from bobocep.exceptions.engine.bobo_producer_queue_full_error import \
    BoboProducerQueueFullError


class BoboProducer(BoboEngineTask, BoboDeciderSubscriber):
    _STR_EXC_QUEUE_FULL = "Queue is full (max size: {})"

    def __init__(self,
                 max_size: int):
        super().__init__()
        self._max_size = max_size
        self._queue = Queue(maxsize=self._max_size)
        self._lock = RLock()

    def update(self) -> None:
        pass  # todo

    def on_decider_completed_run(self, run: BoboDeciderRun):
        with self._lock:
            if not self._queue.full():
                try:
                    self._queue.put(run)
                except Full:
                    raise BoboProducerQueueFullError(
                        self._STR_EXC_QUEUE_FULL.format(self._max_size))
            else:
                raise BoboProducerQueueFullError(
                    self._STR_EXC_QUEUE_FULL.format(self._max_size))