from threading import RLock
from typing import List, Tuple

from bobocep.cep.engine.decider.runtup import BoboRunTuple
from bobocep.dist.dist import BoboDistributedError

"""
Devices on the network.
"""

_EXC_ADDR_LEN = "address must have a length greater than 0"
_EXC_ADDR_SPACE = "address must not contain any spaces"
_EXC_PORT_RANGE = "port must be between 1 and 65535 (inclusive)"
_EXC_URN_LEN = "URN must have a length greater than 0"
_EXC_URN_SPACE = "URN must not contain any spaces"
_EXC_KEY_LEN = "ID key must have a length greater than 0"
_EXC_KEY_SPACE = "ID key must not contain any spaces"


class BoboDevice:
    """
    Contains information about a BoboCEP instance on the network.
    """

    def __init__(self,
                 addr: str,
                 port: int,
                 urn: str,
                 id_key: str):
        super().__init__()
        self._lock: RLock = RLock()

        addr = addr.strip()

        if len(addr) == 0:
            raise BoboDistributedError(_EXC_ADDR_LEN)

        if ' ' in addr:
            raise BoboDistributedError(_EXC_ADDR_SPACE)

        if not (1 <= port <= 65535):
            raise BoboDistributedError(_EXC_URN_LEN)

        urn = urn.strip()

        if len(urn) == 0:
            raise BoboDistributedError(_EXC_URN_LEN)

        if ' ' in urn:
            raise BoboDistributedError(_EXC_URN_SPACE)

        id_key = id_key.strip()

        if len(id_key) == 0:
            raise BoboDistributedError(_EXC_KEY_LEN)

        if ' ' in id_key:
            raise BoboDistributedError(_EXC_KEY_SPACE)

        self._addr: str = addr
        self._port: int = port
        self._urn: str = urn
        self._id_key: str = id_key

    @property
    def addr(self) -> str:
        with self._lock:
            return self._addr

    @addr.setter
    def addr(self, addr: str) -> None:
        with self._lock:
            addr = addr.strip()

            if len(addr) == 0:
                raise BoboDistributedError(_EXC_ADDR_LEN)

            if ' ' in addr:
                raise BoboDistributedError(_EXC_ADDR_SPACE)

            self._addr = addr

    @property
    def port(self) -> int:
        return self._port

    @property
    def urn(self) -> str:
        return self._urn

    @property
    def id_key(self) -> str:
        return self._id_key


class BoboDeviceManager:
    """
    Manages information about a BoboCEP device on the network.
    """

    def __init__(self,
                 device: BoboDevice,
                 flag_reset: bool):
        """
        :param device: The device to manage.
        :param flag_reset: If `True`, it indicates to the BoboDistributed
            instance that the next message to the device should set a flag to
            reset its data on the sending device;
            'False' indicates that no flag should be set.
        """
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
        """
        :return: Device address.
        """
        with self._lock:
            return self._device.addr

    @addr.setter
    def addr(self, addr: str) -> None:
        with self._lock:
            self._device.addr = addr

    @property
    def port(self) -> int:
        """
        :return: Device port.
        """
        return self._device.port

    @property
    def urn(self) -> str:
        """
        :return: Device URN.
        """
        return self._device.urn

    @property
    def id_key(self) -> str:
        """
        :return: Device ID key.
        """
        return self._device.id_key

    @property
    def flag_reset(self) -> bool:
        """
        :return: `True` if reset flag should be set; `False` otherwise.
        """
        with self._lock:
            return self._flag_reset

    @flag_reset.setter
    def flag_reset(self, flag_reset: bool) -> None:
        with self._lock:
            self._flag_reset = flag_reset

    @property
    def last_comms(self) -> int:
        """
        :return: Time of last communication with device.
        """
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
        """
        :return: Time of last communication attempt with device.
        """
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
