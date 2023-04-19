# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
AES encryption for distributed traffic.
"""
from threading import RLock

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from bobocep.dist.crypto.crypto import BoboDistributedCrypto, \
    BoboDistributedCryptoError

_UTF_8: str = "UTF-8"
_PAD_MODULO: int = 16
_END_BYTES: bytes = "BOBO".encode(_UTF_8)
_LEN_END_BYTES: int = len(_END_BYTES)
_PAD_CHAR: str = '\0'

_BYTES_AES_128: int = 16
_BYTES_AES_192: int = 24
_BYTES_AES_256: int = 32


class BoboDistributedCryptoAES(BoboDistributedCrypto):
    """
    AES encryption in GCM mode.
    Data are encrypted using either AES-128, AES-192, or AES-256 encryption.
    """

    def __init__(self,
                 aes_key: str,
                 nonce_length: int = 16,
                 mac_length: int = 16):
        """
        :param aes_key: The AES key to use for encryption.
        :param nonce_length: The nonce length.
        :param mac_length: The MAC length.
        """
        super().__init__()
        self._lock: RLock = RLock()

        # Check AES key
        num_bytes_aes_key = len(aes_key)
        if (num_bytes_aes_key != _BYTES_AES_128 and
                num_bytes_aes_key != _BYTES_AES_192 and
                num_bytes_aes_key != _BYTES_AES_256):
            raise BoboDistributedCryptoError(
                "AES key must be 16, 24, or 32 bytes long "
                "(respectively for AES-128, AES-192, or AES-256): "
                "'{}' has {} bytes.".format(aes_key, len(aes_key)))

        self._aes_key: bytes = aes_key.encode(_UTF_8)
        self._nonce_length: int = nonce_length
        self._mac_length: int = mac_length

        self._msg_min_length: int = (
                _PAD_MODULO +
                nonce_length +
                mac_length +
                _LEN_END_BYTES
        )

    def end_bytes(self) -> bytes:
        """
        :return: Bytes used to signify the end of every encrypted payload.
        """
        return _END_BYTES

    def min_length(self) -> int:
        """
        :return: The minimum possible length of an encrypted payload,
            in number of bytes.
        """
        return self._msg_min_length

    def encrypt(self, msg_str: str) -> bytes:
        """
        :param msg_str: Wraps JSON string in other data for transit.
        :return: The bytes to transmit.
        """
        nonce = get_random_bytes(self._nonce_length)
        cipher = AES.new(self._aes_key, AES.MODE_GCM,
                         nonce=nonce, mac_len=self._mac_length)

        # Pad message, if necessary
        len_msg = len(msg_str)
        if len_msg % _PAD_MODULO != 0:
            msg_str = msg_str + \
                      (_PAD_CHAR * (_PAD_MODULO - len_msg % _PAD_MODULO))

        ciphertext, mac = cipher.encrypt_and_digest(  # type: ignore
            msg_str.encode(_UTF_8))

        # Append nonce, mac, and end bytes to ciphertext
        ciphertext_bytes = bytearray(ciphertext)
        ciphertext_bytes.extend(nonce)
        ciphertext_bytes.extend(mac)
        ciphertext_bytes.extend(_END_BYTES)

        return ciphertext_bytes

    def decrypt(self, msg_bytes: bytes) -> str:
        """
        :param msg_bytes: Incoming bytes.
        :return: Incoming JSON string with other data from transit.
        """

        # [CIPHERTEXT][NONCE][MAC][END_BYTES]
        ciphertext = msg_bytes[:-(
                self._nonce_length + self._mac_length + _LEN_END_BYTES)]
        nonce = msg_bytes[
                -(self._nonce_length + self._mac_length + _LEN_END_BYTES):
                -(self._mac_length + _LEN_END_BYTES)]
        mac = msg_bytes[
              -(self._mac_length + _LEN_END_BYTES):
              -_LEN_END_BYTES]

        cipher = AES.new(self._aes_key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(  # type: ignore
            ciphertext, mac).decode(_UTF_8).rstrip(_PAD_CHAR)

        return plaintext
