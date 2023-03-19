# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from threading import RLock
from typing import List, Tuple

from bobocep.cep.engine.decider import BoboRunTuple
from bobocep.dist import BoboDevice


class _BoboDeviceManager:
    """
    Manages information about a BoboCEP instance on the network.
    """

    def __init__(self,
                 device: BoboDevice,
                 flag_reset: bool):
        super().__init__()
        self._lock: RLock = RLock()

        self._device: BoboDevice = device
        self._flag_reset: bool = flag_reset

        self._last_comms: int = 0
        self._last_attempt: int = 0

        self._stash_completed: List[BoboRunTuple] = []
        self._stash_halted: List[BoboRunTuple] = []
        self._stash_updated: List[BoboRunTuple] = []

    @property
    def addr(self) -> str:
        with self._lock:
            return self._device.addr

    @addr.setter
    def addr(self, addr: str) -> None:
        with self._lock:
            self._device.addr = addr

    @property
    def port(self) -> int:
        return self._device.port

    @property
    def urn(self) -> str:
        return self._device.urn

    @property
    def id_key(self) -> str:
        return self._device.id_key

    @property
    def flag_reset(self) -> bool:
        with self._lock:
            return self._flag_reset

    @flag_reset.setter
    def flag_reset(self, flag_reset: bool) -> None:
        with self._lock:
            self._flag_reset = flag_reset

    @property
    def last_comms(self) -> int:
        with self._lock:
            return self._last_comms

    @last_comms.setter
    def last_comms(self, last_comms: int) -> None:
        with self._lock:
            self._last_comms = max(0, last_comms)

    @property
    def last_attempt(self) -> int:
        with self._lock:
            return self._last_attempt

    @last_attempt.setter
    def last_attempt(self, last_attempt: int) -> None:
        with self._lock:
            self._last_attempt = max(0, last_attempt)

    def reset_last(self) -> None:
        with self._lock:
            self._last_comms = 0
            self._last_attempt = 0

    def stash(self) -> Tuple[List[BoboRunTuple],
                             List[BoboRunTuple],
                             List[BoboRunTuple]]:
        with self._lock:
            return self._stash_completed, \
                   self._stash_halted, \
                   self._stash_updated

    def append_stash(self,
                     completed: List[BoboRunTuple],
                     halted: List[BoboRunTuple],
                     updated: List[BoboRunTuple]):
        with self._lock:
            self._stash_completed.extend(completed)
            self._stash_halted.extend(halted)
            self._stash_updated.extend(updated)

    def size_stash(self) -> int:
        with self._lock:
            return len(self._stash_completed) + \
                   len(self._stash_halted) + \
                   len(self._stash_updated)

    def clear_stash(self) -> None:
        with self._lock:
            self._stash_completed = []
            self._stash_halted = []
            self._stash_updated = []
