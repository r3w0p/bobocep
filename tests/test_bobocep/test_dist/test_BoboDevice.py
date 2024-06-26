# Copyright (c) 2019-2024 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

from bobocep.dist.device import BoboDevice
from bobocep.dist.device import BoboDeviceError


class TestValid:

    def test_properties(self):
        addr = "127.0.0.1"
        port = 8080
        urn = "urn:test"
        id_key = "abc123"

        device = BoboDevice(
            addr=addr,
            port=port,
            urn=urn,
            id_key=id_key)

        assert device.addr == addr
        assert device.port == port
        assert device.urn == urn
        assert device.id_key == id_key

    def test_set_addr(self):
        addr_original = "127.0.0.1"
        addr_new = "192.168.1.3"

        device = BoboDevice(
            addr=addr_original,
            port=8080,
            urn="urn:test",
            id_key="abc123")

        assert device.addr == addr_original

        device.addr = addr_new

        assert device.addr == addr_new


class TestInvalid:

    def test_addr_length_0(self):
        with pytest.raises(BoboDeviceError):
            BoboDevice(
                addr="",
                port=8080,
                urn="urn:test",
                id_key="abc123")

    def test_addr_contains_inner_space(self):
        with pytest.raises(BoboDeviceError):
            BoboDevice(
                addr="127 1",
                port=8080,
                urn="urn:test",
                id_key="abc123")

    def test_port_below_1(self):
        with pytest.raises(BoboDeviceError):
            BoboDevice(
                addr="127.0.0.1",
                port=0,
                urn="urn:test",
                id_key="abc123")

    def test_port_above_65535(self):
        with pytest.raises(BoboDeviceError):
            BoboDevice(
                addr="127.0.0.1",
                port=65536,
                urn="urn:test",
                id_key="abc123")

    def test_urn_length_0(self):
        with pytest.raises(BoboDeviceError):
            BoboDevice(
                addr="127.0.0.1",
                port=8080,
                urn="",
                id_key="abc123")

    def test_urn_contains_inner_space(self):
        with pytest.raises(BoboDeviceError):
            BoboDevice(
                addr="127.0.0.1",
                port=8080,
                urn="urn invalid",
                id_key="abc123")

    def test_id_key_length_0(self):
        with pytest.raises(BoboDeviceError):
            BoboDevice(
                addr="127.0.0.1",
                port=8080,
                urn="urn:test",
                id_key="")

    def test_id_key_contains_inner_space(self):
        with pytest.raises(BoboDeviceError):
            BoboDevice(
                addr="127.0.0.1",
                port=8080,
                urn="urn:test",
                id_key="id_key invalid")

    def test_set_addr_length_0(self):
        addr_original = "127.0.0.1"
        addr_new = ""

        device = BoboDevice(
            addr=addr_original,
            port=8080,
            urn="urn:test",
            id_key="abc123")

        with pytest.raises(BoboDeviceError):
            device.addr = addr_new

        assert device.addr == addr_original

    def test_set_addr_contains_inner_space(self):
        addr_original = "127.0.0.1"
        addr_new = "192 2"

        device = BoboDevice(
            addr=addr_original,
            port=8080,
            urn="urn:test",
            id_key="abc123")

        with pytest.raises(BoboDeviceError):
            device.addr = addr_new

        assert device.addr == addr_original
