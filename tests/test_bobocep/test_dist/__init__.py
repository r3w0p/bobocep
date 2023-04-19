# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from threading import RLock
from typing import List

from bobocep.cep.engine.decider.runserial import BoboRunSerial
from bobocep.dist.pubsub import BoboDistributedSubscriber
from bobocep.dist.tcp import BoboDistributedTCP


def tc_run_distributed_tcp(dist: BoboDistributedTCP):
    dist.run()


class StubDistributedSubscriber(BoboDistributedSubscriber):

    def __init__(self):
        super().__init__()
        self._lock: RLock = RLock()

        self._completed: List[BoboRunSerial] = []
        self._halted: List[BoboRunSerial] = []
        self._updated: List[BoboRunSerial] = []

    def on_distributed_update(self,
                              completed: List[BoboRunSerial],
                              halted: List[BoboRunSerial],
                              updated: List[BoboRunSerial]):
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
