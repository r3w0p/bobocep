# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Distributed complex event processing.
"""

from abc import ABC, abstractmethod
from threading import RLock

from bobocep import BoboError
from bobocep.dist.constants import *
from bobocep.dist.pubsub import BoboDistributedPublisher


class BoboDistributedError(BoboError):
    """
    A distributed error.
    """


class BoboDistributedSystemError(BoboDistributedError):
    """
    A distributed system error.
    """


class BoboDistributedTimeoutError(BoboDistributedError):
    """
    A distributed timeout error.
    """


class BoboDistributed(BoboDistributedPublisher, ABC):
    """
    Distributed `BoboCEP`.
    """

    @abstractmethod
    def run(self):
        """"""


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

        if len(addr) == 0:
            raise BoboDistributedError(EXC_ADDR_LEN)

        if ' ' in addr:
            raise BoboDistributedError(EXC_ADDR_SPACE)

        if not (1 <= port <= 65535):
            raise BoboDistributedError(EXC_URN_LEN)

        if len(urn) == 0:
            raise BoboDistributedError(EXC_URN_LEN)

        if ' ' in urn:
            raise BoboDistributedError(EXC_URN_SPACE)

        if len(id_key) == 0:
            raise BoboDistributedError(EXC_KEY_LEN)

        if ' ' in id_key:
            raise BoboDistributedError(EXC_KEY_SPACE)

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
        if len(addr) == 0:
            raise BoboDistributedError(EXC_ADDR_LEN)

        if ' ' in addr:
            raise BoboDistributedError(EXC_ADDR_SPACE)

        with self._lock:
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
