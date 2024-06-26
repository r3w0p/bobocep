# Copyright (c) 2019-2024 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Devices on the network.
"""

from threading import RLock

from bobocep.dist.dist import BoboDistributedError

_EXC_ADDR_LEN = "address must have a length greater than 0"
_EXC_ADDR_SPACE = "address must not contain any spaces"
_EXC_PORT_RANGE = "port must be between 1 and 65535 (inclusive)"
_EXC_URN_LEN = "URN must have a length greater than 0"
_EXC_URN_SPACE = "URN must not contain any spaces"
_EXC_KEY_LEN = "ID key must have a length greater than 0"
_EXC_KEY_SPACE = "ID key must not contain any spaces"


class BoboDeviceError(BoboDistributedError):
    """
    A device error.
    """


class BoboDevice:
    """
    Contains information about a BoboCEP instance on the network.
    """

    def __init__(self,
                 addr: str,
                 port: int,
                 urn: str,
                 id_key: str):
        """
        :param addr: Device address.
        :param port: Device port.
        :param urn: Device URN.
        :param id_key: Device ID key.
        """
        super().__init__()
        self._lock: RLock = RLock()

        addr = addr.strip()

        if len(addr) == 0:
            raise BoboDeviceError(_EXC_ADDR_LEN)

        if ' ' in addr:
            raise BoboDeviceError(_EXC_ADDR_SPACE)

        if not (1 <= port <= 65535):
            raise BoboDeviceError(_EXC_URN_LEN)

        urn = urn.strip()

        if len(urn) == 0:
            raise BoboDeviceError(_EXC_URN_LEN)

        if ' ' in urn:
            raise BoboDeviceError(_EXC_URN_SPACE)

        id_key = id_key.strip()

        if len(id_key) == 0:
            raise BoboDeviceError(_EXC_KEY_LEN)

        if ' ' in id_key:
            raise BoboDeviceError(_EXC_KEY_SPACE)

        self._addr: str = addr
        self._port: int = port
        self._urn: str = urn
        self._id_key: str = id_key

    @property
    def addr(self) -> str:
        """
        :return: Device address.
        """
        with self._lock:
            return self._addr

    @addr.setter
    def addr(self, addr: str) -> None:
        """
        Set device address.

        :param addr: The new address.
        """
        with self._lock:
            addr = addr.strip()

            if len(addr) == 0:
                raise BoboDeviceError(_EXC_ADDR_LEN)

            if ' ' in addr:
                raise BoboDeviceError(_EXC_ADDR_SPACE)

            self._addr = addr

    @property
    def port(self) -> int:
        """
        :return: Device port.
        """
        return self._port

    @property
    def urn(self) -> str:
        """
        :return: Device URN.
        """
        return self._urn

    @property
    def id_key(self) -> str:
        """
        :return: Device ID key.
        """
        return self._id_key
