# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from bobocep.dist.device import BoboDevice
from bobocep.dist.devman import BoboDeviceManager
from tests.test_bobocep.test_cep.test_engine.test_decider import tc_run_tuple


class TestValid:

    def test_properties_from_device(self):
        device = BoboDevice(
            addr="127.0.0.1",
            port=8080,
            urn="test_urn",
            id_key="test_id_key")

        manager = BoboDeviceManager(
            device=device,
            flag_reset=False)

        assert manager.addr == device.addr
        assert manager.port == device.port
        assert manager.urn == device.urn
        assert manager.id_key == device.id_key

    def test_last_reset_true_then_set_to_false(self):
        manager = BoboDeviceManager(
            device=BoboDevice(
                addr="127.0.0.1",
                port=8080,
                urn="test_urn",
                id_key="test_id_key"),
            flag_reset=True)

        assert manager.flag_reset is True

        manager.flag_reset = False

        assert manager.flag_reset is False

    def test_last_comms_0_then_set_to_1(self):
        manager = BoboDeviceManager(
            device=BoboDevice(
                addr="127.0.0.1",
                port=8080,
                urn="test_urn",
                id_key="test_id_key"),
            flag_reset=True)

        assert manager.last_comms == 0

        manager.last_comms = 1

        assert manager.last_comms == 1

    def test_last_attempt_0_then_set_to_1(self):
        manager = BoboDeviceManager(
            device=BoboDevice(
                addr="127.0.0.1",
                port=8080,
                urn="test_urn",
                id_key="test_id_key"),
            flag_reset=True)

        assert manager.last_attempt == 0

        manager.last_attempt = 1

        assert manager.last_attempt == 1

    def test_reset_last(self):
        manager = BoboDeviceManager(
            device=BoboDevice(
                addr="127.0.0.1",
                port=8080,
                urn="test_urn",
                id_key="test_id_key"),
            flag_reset=True)

        manager.last_comms = 1
        manager.last_attempt = 1

        manager.reset_last()

        assert manager.last_comms == 0
        assert manager.last_attempt == 0

    def test_set_addr(self):
        orig_addr: str = "127.0.0.1"
        new_addr: str = "192.168.1.1"

        device = BoboDevice(
            addr=orig_addr,
            port=8080,
            urn="test_urn",
            id_key="test_id_key")

        manager = BoboDeviceManager(
            device=device,
            flag_reset=True)

        assert device.addr == orig_addr
        assert manager.addr == orig_addr

        manager.addr = new_addr

        assert device.addr == new_addr
        assert manager.addr == new_addr

    def test_stash(self):
        manager = BoboDeviceManager(
            device=BoboDevice(
                addr="127.0.0.1",
                port=8080,
                urn="test_urn",
                id_key="test_id_key"),
            flag_reset=True)

        assert manager.size_stash() == 0

        completed = [tc_run_tuple(run_id="run_completed")]
        halted = [tc_run_tuple(run_id="run_halted")]
        updated = [tc_run_tuple(run_id="run_updated")]

        manager.append_stash(
            completed=completed,
            halted=halted,
            updated=updated
        )

        stash_completed, stash_halted, stash_updated = manager.stash()

        assert len(stash_completed) == 1
        assert stash_completed[0].run_id == completed[0].run_id

        assert len(stash_halted) == 1
        assert stash_halted[0].run_id == halted[0].run_id

        assert len(stash_updated) == 1
        assert stash_updated[0].run_id == updated[0].run_id

    def test_append_then_size_then_clear(self):
        manager = BoboDeviceManager(
            device=BoboDevice(
                addr="127.0.0.1",
                port=8080,
                urn="test_urn",
                id_key="test_id_key"),
            flag_reset=True)

        assert manager.size_stash() == 0

        manager.append_stash(
            completed=[tc_run_tuple()],
            halted=[tc_run_tuple()],
            updated=[tc_run_tuple()]
        )

        assert manager.size_stash() == 3

        manager.clear_stash()

        assert manager.size_stash() == 0
