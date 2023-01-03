# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.


class BoboDeviceTuple:
    """A tuple that contains information about a BoboCEP instance on the
    network."""

    def __init__(self,
                 addr: str,
                 port: int,
                 urn: str,
                 id_key: str):
        super().__init__()

        # TODO validation + setter validation

        self._addr: str = addr
        self._port: int = port
        self._urn: str = urn
        self._id_key: str = id_key

    @property
    def addr(self) -> str:
        return self._addr

    @addr.setter
    def addr(self, addr: str) -> None:
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
