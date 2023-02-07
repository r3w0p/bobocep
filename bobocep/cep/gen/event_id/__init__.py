# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""BoboEvent ID generators."""

from abc import ABC, abstractmethod
from threading import RLock
from time import time
from typing import Optional


class BoboGenEventID(ABC):
    """An event ID generator."""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def generate(self) -> str:
        """"""


class BoboGenEventIDUnique(BoboGenEventID):
    """An event ID generator that always generates a unique,
    non-repeating ID."""

    def __init__(self, urn: Optional[str] = None):
        super().__init__()
        self._lock: RLock = RLock()

        self._last: int = 0
        self._count: int = 0
        self._urn: Optional[str] = urn

    def generate(self) -> str:
        with self._lock:
            now: int = int(time())

            if now == self._last:
                self._count += 1
            else:
                self._count = 0
                self._last = now

            if self._urn is not None:
                return "{}_{}_{}".format(self._urn, now, self._count)
            else:
                return "{}_{}".format(now, self._count)
