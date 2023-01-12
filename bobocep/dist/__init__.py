# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""Distributed complex event processing."""

from abc import ABC, abstractmethod

from bobocep import BoboError
from bobocep.cep.engine.task.decider.pubsub import BoboDeciderSubscriber
from bobocep.cep.engine.task.forwarder.pubsub import BoboForwarderSubscriber
from bobocep.cep.engine.task.producer.pubsub import BoboProducerSubscriber
from bobocep.cep.engine.task.receiver.pubsub import BoboReceiverSubscriber
from bobocep.dist.pubsub import BoboDistributedPublisher


class BoboDistributedError(BoboError):
    """A distributed error."""


class BoboDistributedSystemError(BoboDistributedError):
    """A distributed system error."""


class BoboDistributedTimeoutError(BoboDistributedError):
    """A distributed timeout error."""


class BoboDeviceTuple:
    """A tuple that contains information about a BoboCEP instance on the
    network."""

    def __init__(self,
                 addr: str,
                 port: int,
                 urn: str,
                 id_key: str):
        super().__init__()

        # TODO validation + setters

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


class BoboDistributed(BoboDistributedPublisher,
                      BoboReceiverSubscriber,
                      BoboDeciderSubscriber,
                      BoboProducerSubscriber,
                      BoboForwarderSubscriber,
                      ABC):
    """A class for enabling `BoboCEP` to be distributed over the network."""

    @abstractmethod
    def run(self):
        """"""
