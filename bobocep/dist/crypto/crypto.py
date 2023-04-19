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
    """
    Abstract class for distributed crypto.
    """

    @abstractmethod
    def encrypt(self, msg_str: str) -> bytes:
        """
        :param msg_str: Message to encrypt.
        :return: Encrypted message.
        """

    @abstractmethod
    def decrypt(self, msg_bytes: bytes) -> str:
        """
        :param msg_bytes: Message to decrypt.
        :return: Decrypted message.
        """

    @abstractmethod
    def end_bytes(self) -> bytes:
        """
        :return: Bytes used to signify the end of every encrypted payload.
        """

    @abstractmethod
    def min_length(self) -> int:
        """
        :return: The minimum possible length of an encrypted payload,
            in number of bytes.
        """
