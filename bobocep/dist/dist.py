# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Distributed complex event processing.
"""

from abc import ABC, abstractmethod

from bobocep import BoboError
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
    def run(self) -> None:
        """
        Runs distributed.
        """
