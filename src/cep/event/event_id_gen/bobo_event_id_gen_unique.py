# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from threading import RLock
from time import time

from src.cep.event.event_id_gen.bobo_event_id_gen import \
    BoboEventIDGen


class BoboEventIDGenUnique(BoboEventIDGen):
    """An event ID generator that always generates a unique,
    non-repeating ID."""

    def __init__(self):
        super().__init__()
        self._lock: RLock = RLock()

        self._last: int = 0
        self._count: int = 0

    def generate(self) -> str:
        with self._lock:
            now: int = int(time())

            if now == self._last:
                self._count += 1
            else:
                self._count = 0
                self._last = now

            return "{}_{}".format(now, self._count)
