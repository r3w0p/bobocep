from threading import RLock
from typing import List

from bobocep.cep.engine.decider.runtup import BoboRunTuple
from bobocep.dist.pubsub import BoboDistributedSubscriber
from bobocep.dist.tcp import BoboDistributedTCP


def tc_run_distributed_tcp(dist: BoboDistributedTCP):
    dist.run()


class StubDistributedSubscriber(BoboDistributedSubscriber):

    def __init__(self):
        super().__init__()
        self._lock: RLock = RLock()

        self._completed: List[BoboRunTuple] = []
        self._halted: List[BoboRunTuple] = []
        self._updated: List[BoboRunTuple] = []

    def on_distributed_update(self,
                              completed: List[BoboRunTuple],
                              halted: List[BoboRunTuple],
                              updated: List[BoboRunTuple]):
        with self._lock:
            self._completed += completed
            self._halted += halted
            self._updated += updated

    @property
    def completed(self):
        with self._lock:
            return self._completed

    @property
    def halted(self):
        with self._lock:
            return self._halted

    @property
    def updated(self):
        with self._lock:
            return self._updated
