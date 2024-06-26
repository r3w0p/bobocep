# Copyright (c) 2019-2024 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Distributed complex event processing.
"""

from abc import ABC, abstractmethod

from bobocep import BoboError


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


class BoboDistributedJSONError(BoboDistributedError):
    """
    A distributed JSON error.
    """


class BoboDistributedJSONEncodeError(BoboDistributedJSONError):
    """
    A distributed JSON encode error.
    """


class BoboDistributedJSONDecodeError(BoboDistributedJSONError):
    """
    A distributed JSON decode error.
    """


class BoboDistributed(ABC):
    """
    Distributed `BoboCEP`.
    """

    @abstractmethod
    def run(self) -> None:
        """
        Runs distributed.
        """
