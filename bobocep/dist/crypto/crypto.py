# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Encryption for distributed `BoboCEP`.
"""

from abc import ABC, abstractmethod

from bobocep.dist.dist import BoboDistributedError


class BoboDistributedCryptoError(BoboDistributedError):
    """
    A distributed crypto error.
    """


class BoboDistributedCrypto(ABC):

    @abstractmethod
    def encrypt(self, msg_str: str) -> bytes:
        """"""

    @abstractmethod
    def decrypt(self, msg_bytes: bytes) -> str:
        """"""

    @abstractmethod
    def end_bytes(self) -> bytes:
        """
        :return: The bytes used to signify the end of ciphertext output.
        """

    @abstractmethod
    def min_length(self) -> int:
        """
        :return: The minimum length of ciphertext output.
        """
