# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

from bobocep.dist.crypto.aes import BoboDistributedCryptoAES
from bobocep.dist.crypto.crypto import BoboDistributedCryptoError


class TestValid:

    def test_encrypt_aes_key_16(self):
        crypto = BoboDistributedCryptoAES(aes_key="1234567890123456")

        plaintext: str = "test_plaintext"
        ciphertext: bytes = crypto.encrypt(plaintext)
        decrypted: str = crypto.decrypt(ciphertext)

        assert plaintext == decrypted

    def test_encrypt_aes_key_24(self):
        crypto = BoboDistributedCryptoAES(aes_key="123456789012345678901234")

        plaintext: str = "test_plaintext"
        ciphertext: bytes = crypto.encrypt(plaintext)
        decrypted: str = crypto.decrypt(ciphertext)

        assert plaintext == decrypted

    def test_encrypt_aes_key_32(self):
        crypto = BoboDistributedCryptoAES(
            aes_key="12345678901234567890123456789012")

        plaintext: str = "test_plaintext"
        ciphertext: bytes = crypto.encrypt(plaintext)
        decrypted: str = crypto.decrypt(ciphertext)

        assert plaintext == decrypted

    def test_encrypt_empty_string(self):
        crypto = BoboDistributedCryptoAES(aes_key="1234567890123456")

        plaintext: str = ""
        ciphertext: bytes = crypto.encrypt(plaintext)
        decrypted: str = crypto.decrypt(ciphertext)

        assert plaintext == decrypted

    def test_encrypt_string_length_1(self):
        crypto = BoboDistributedCryptoAES(aes_key="1234567890123456")

        plaintext: str = "a"
        ciphertext: bytes = crypto.encrypt(plaintext)
        decrypted: str = crypto.decrypt(ciphertext)

        assert plaintext == decrypted


class TestInvalid:

    def test_aes_key_empty(self):
        with pytest.raises(BoboDistributedCryptoError):
            BoboDistributedCryptoAES(aes_key="")

    def test_aes_key_lt_16(self):
        with pytest.raises(BoboDistributedCryptoError):
            BoboDistributedCryptoAES(aes_key="1234567890")

    def test_aes_key_gt_16_lt_24(self):
        with pytest.raises(BoboDistributedCryptoError):
            BoboDistributedCryptoAES(aes_key="12345678901234567890")

    def test_aes_key_gt_24_lt_32(self):
        with pytest.raises(BoboDistributedCryptoError):
            BoboDistributedCryptoAES(
                aes_key="123456789012345678901234567890")

    def test_aes_key_gt_32(self):
        with pytest.raises(BoboDistributedCryptoError):
            BoboDistributedCryptoAES(
                aes_key="1234567890123456789012345678901234567890")
