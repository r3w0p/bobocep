# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
import logging
from threading import Thread
from time import sleep
from typing import List

import pytest

from bobocep.cep.engine.decider.runserial import BoboRunSerial
from bobocep.dist.crypto.aes import BoboDistributedCryptoAES
from bobocep.dist.device import BoboDevice
from bobocep.dist.dist import BoboDistributedError
from bobocep.dist.tcp import BoboDistributedTCP
from tests.test_bobocep.test_cep.test_engine.test_decider import tc_run_simple, \
    tc_decider_sub
from tests.test_bobocep.test_cep.test_event import tc_event_simple
from tests.test_bobocep.test_cep.test_phenomenon import tc_pattern, \
    tc_phenomenon
from tests.test_bobocep.test_dist import StubDistributedSubscriber, \
    tc_run_distributed_tcp


# GitHub Actions: "OSError: [Errno 98] Address already in use"
# Use a different port for each running dist in this file: 8080, 8081, 8082...


class TestValid:

    def test_sync_1c_1h_1u_1remote_aes(self):
        logging.getLogger().setLevel(logging.DEBUG)

        completed: List[BoboRunSerial] = [
            tc_run_simple(
                tc_pattern(name="pattern_completed"),
                tc_event_simple(event_id="event_id_completed"),
                run_id="run_id_completed",
                phenomenon_name="phenom_name_completed",
                block_index=1
            ).serialize()]

        halted: List[BoboRunSerial] = [
            tc_run_simple(
                tc_pattern(name="pattern_halted"),
                tc_event_simple(event_id="event_id_halted"),
                run_id="run_id_halted",
                phenomenon_name="phenom_name_halted",
                block_index=1
            ).serialize()]

        updated: List[BoboRunSerial] = [
            tc_run_simple(
                tc_pattern(name="pattern_updated"),
                tc_event_simple(event_id="event_id_updated"),
                run_id="run_id_updated",
                phenomenon_name="phenom_name_updated",
                block_index=1
            ).serialize()]

        devices = [
            BoboDevice(
                addr="127.0.0.1",
                port=8080,
                urn="urn:dist:1",
                id_key="1111111111"),
            BoboDevice(
                addr="127.0.0.1",
                port=8080,
                urn="urn:dist:2",
                id_key="2222222222")
        ]

        decider, dec_sub = tc_decider_sub([tc_phenomenon()])

        dist = BoboDistributedTCP(
            urn="urn:dist:1",
            decider=decider,
            devices=devices,
            crypto=BoboDistributedCryptoAES("1234567890ABCDEF"),
            period_ping=30,
            period_resync=60,
            flag_reset=False  # to prevent initial FORCE_RESYNC
        )

        dist_sub = StubDistributedSubscriber()
        dist.subscribe(dist_sub)

        # Sets Device 2 to within "SYNC Period"
        last_comms = BoboDistributedTCP._now()
        dist._devices[devices[1].urn].last_comms = last_comms

        t = Thread(target=tc_run_distributed_tcp, args=[dist])
        t.start()

        sleep(1)

        dist.on_decider_update(
            completed=completed,
            halted=halted,
            updated=updated)

        sleep(3)

        dist.close()
        dist.join()
        t.join()
        assert dist.is_closed()

        assert dist.size_incoming() == 0
        assert dist.size_outgoing() == 0

        assert len(dist_sub.completed) == 1
        assert len(dist_sub.halted) == 1
        assert len(dist_sub.updated) == 1

        for idistsub, irun in [
            (dist_sub.completed, completed),
            (dist_sub.halted, halted),
            (dist_sub.updated, updated),
        ]:
            assert idistsub[0].run_id == irun[0].run_id
            assert idistsub[0].phenomenon_name == irun[0].phenomenon_name
            assert idistsub[0].pattern_name == irun[0].pattern_name
            assert idistsub[0].block_index == irun[0].block_index
            assert idistsub[0].history.size() == 1 and \
                   irun[0].history.size() == 1
            assert idistsub[0].history.all_events()[0].event_id == \
                   irun[0].history.all_events()[0].event_id

    def test_ping_aes(self):
        logging.getLogger().setLevel(logging.DEBUG)

        devices = [
            BoboDevice(
                addr="127.0.0.1",
                port=8081,
                urn="urn:dist:1",
                id_key="1111111111"),
            BoboDevice(
                addr="127.0.0.1",
                port=8081,
                urn="urn:dist:2",
                id_key="2222222222")
        ]

        decider, dec_sub = tc_decider_sub([tc_phenomenon()])

        dist = BoboDistributedTCP(
            urn="urn:dist:1",
            decider=decider,
            devices=devices,
            crypto=BoboDistributedCryptoAES("1234567890ABCDEF"),
            period_ping=30,
            period_resync=60,
            flag_reset=False  # to prevent initial FORCE_RESYNC
        )

        dist_sub = StubDistributedSubscriber()
        dist.subscribe(dist_sub)

        # Sets Device 2 to within "PING Period"
        last_comms = BoboDistributedTCP._now() - 35
        dist._devices[devices[1].urn].last_comms = last_comms

        t = Thread(target=tc_run_distributed_tcp, args=[dist])
        t.start()

        sleep(3)

        dist.close()
        dist.join()
        t.join()
        assert dist.is_closed()

        # "Remote device" now within "SYNC Period"
        assert dist._devices[devices[1].urn].last_comms > last_comms

    def test_resync_1c_1h_1u_1remote_aes(self):
        # This test is for being in the "RESYNC Period",
        # NOT the FORCE_RESYNC flag
        logging.getLogger().setLevel(logging.DEBUG)

        completed: List[BoboRunSerial] = [
            tc_run_simple(
                tc_pattern(name="pattern_completed"),
                tc_event_simple(event_id="event_id_completed"),
                run_id="run_id_completed",
                phenomenon_name="phenom_name_completed",
                block_index=1
            ).serialize()]

        halted: List[BoboRunSerial] = [
            tc_run_simple(
                tc_pattern(name="pattern_halted"),
                tc_event_simple(event_id="event_id_halted"),
                run_id="run_id_halted",
                phenomenon_name="phenom_name_halted",
                block_index=1
            ).serialize()]

        updated: List[BoboRunSerial] = [
            tc_run_simple(
                tc_pattern(name="pattern_updated"),
                tc_event_simple(event_id="event_id_updated"),
                run_id="run_id_updated",
                phenomenon_name="phenom_name_updated",
                block_index=1
            ).serialize()]

        devices = [
            BoboDevice(
                addr="127.0.0.1",
                port=8082,
                urn="urn:dist:1",
                id_key="1111111111"),
            BoboDevice(
                addr="127.0.0.1",
                port=8082,
                urn="urn:dist:2",
                id_key="2222222222")
        ]

        decider, dec_sub = tc_decider_sub([tc_phenomenon()])

        dist = BoboDistributedTCP(
            urn="urn:dist:1",
            decider=decider,
            devices=devices,
            crypto=BoboDistributedCryptoAES("1234567890ABCDEF"),
            period_ping=30,
            period_resync=60,
            flag_reset=False  # to prevent initial FORCE_RESYNC
        )

        dist_sub = StubDistributedSubscriber()
        dist.subscribe(dist_sub)

        # Sets Device 2 to within "RESYNC Period"
        last_comms = BoboDistributedTCP._now() - 65
        dist._devices[devices[1].urn].last_comms = last_comms

        t = Thread(target=tc_run_distributed_tcp, args=[dist])
        t.start()

        sleep(1)

        dist.on_decider_update(
            completed=completed,
            halted=halted,
            updated=updated)

        sleep(3)

        dist.close()
        dist.join()
        t.join()
        assert dist.is_closed()

        assert dist.size_incoming() == 0
        assert dist.size_outgoing() == 0

        assert len(dist_sub.completed) == 1
        assert len(dist_sub.halted) == 1
        assert len(dist_sub.updated) == 1

    def test_flag_reset_1c_1h_1u_1remote_aes(self):
        logging.getLogger().setLevel(logging.DEBUG)

        completed: List[BoboRunSerial] = [
            tc_run_simple(
                tc_pattern(name="pattern_completed"),
                tc_event_simple(event_id="event_id_completed"),
                run_id="run_id_completed",
                phenomenon_name="phenom_name_completed",
                block_index=1
            ).serialize()]

        halted: List[BoboRunSerial] = [
            tc_run_simple(
                tc_pattern(name="pattern_halted"),
                tc_event_simple(event_id="event_id_halted"),
                run_id="run_id_halted",
                phenomenon_name="phenom_name_halted",
                block_index=1
            ).serialize()]

        updated: List[BoboRunSerial] = [
            tc_run_simple(
                tc_pattern(name="pattern_updated"),
                tc_event_simple(event_id="event_id_updated"),
                run_id="run_id_updated",
                phenomenon_name="phenom_name_updated",
                block_index=1
            ).serialize()]

        devices = [
            BoboDevice(
                addr="127.0.0.1",
                port=8083,
                urn="urn:dist:1",
                id_key="1111111111"),
            BoboDevice(
                addr="127.0.0.1",
                port=8083,
                urn="urn:dist:2",
                id_key="2222222222")
        ]

        decider, dec_sub = tc_decider_sub([tc_phenomenon()])

        dist = BoboDistributedTCP(
            urn="urn:dist:1",
            decider=decider,
            devices=devices,
            crypto=BoboDistributedCryptoAES("1234567890ABCDEF"),
            period_ping=30,
            period_resync=60,
            flag_reset=True  # trigger initial FORCE_RESYNC
        )

        dist_sub = StubDistributedSubscriber()
        dist.subscribe(dist_sub)

        # Sets both Devices to within "OK Period"
        last_time = BoboDistributedTCP._now()
        dist._devices[devices[0].urn].last_comms = last_time
        dist._devices[devices[0].urn].last_attempt = last_time
        dist._devices[devices[1].urn].last_comms = last_time
        dist._devices[devices[1].urn].last_attempt = last_time

        t = Thread(target=tc_run_distributed_tcp, args=[dist])
        t.start()

        sleep(1)

        dist.on_decider_update(
            completed=completed,
            halted=halted,
            updated=updated)

        sleep(3)

        dist.close()
        dist.join()
        t.join()
        assert dist.is_closed()

        # Device 2 should have reset the comms for Device 1 to force a resync
        assert dist._devices[devices[0].urn].last_comms == 0
        assert dist._devices[devices[0].urn].last_attempt == 0

    def test_close_on_closed(self):
        logging.getLogger().setLevel(logging.DEBUG)

        devices = [
            BoboDevice(
                addr="127.0.0.1",
                port=8084,
                urn="urn:dist:1",
                id_key="1111111111"),
            BoboDevice(
                addr="127.0.0.1",
                port=8084,
                urn="urn:dist:2",
                id_key="2222222222")
        ]

        decider, dec_sub = tc_decider_sub([tc_phenomenon()])

        dist = BoboDistributedTCP(
            urn="urn:dist:1",
            decider=decider,
            devices=devices,
            crypto=BoboDistributedCryptoAES("1234567890ABCDEF"),
            period_ping=30,
            period_resync=60,
            flag_reset=True  # trigger initial FORCE_RESYNC
        )

        assert dist.close() is None
        assert dist.is_closed()

        # Should be an idempotent operation
        assert dist.close() is None

    # TODO "Update address if remote address has changed"
    # TODO ping with RESET FLAG


class TestInvalid:

    def test_duplicate_urns_in_devices(self):
        logging.getLogger().setLevel(logging.DEBUG)

        devices = [
            BoboDevice(
                addr="127.0.0.1",
                port=8085,
                urn="urn:dist:duplicate",
                id_key="1111111111"),
            BoboDevice(
                addr="127.0.0.1",
                port=8085,
                urn="urn:dist:duplicate",
                id_key="2222222222")
        ]

        decider, dec_sub = tc_decider_sub([tc_phenomenon()])

        with pytest.raises(BoboDistributedError):
            BoboDistributedTCP(
                urn="urn:dist:duplicate",
                decider=decider,
                devices=devices,
                crypto=BoboDistributedCryptoAES("1234567890ABCDEF")
            )

    def test_no_devices_listed(self):
        logging.getLogger().setLevel(logging.DEBUG)

        devices = []

        decider, dec_sub = tc_decider_sub([tc_phenomenon()])

        with pytest.raises(BoboDistributedError):
            BoboDistributedTCP(
                urn="urn:dist:1",
                decider=decider,
                devices=devices,
                crypto=BoboDistributedCryptoAES("1234567890ABCDEF")
            )

    def test_device_not_listed_in_devices(self):
        logging.getLogger().setLevel(logging.DEBUG)

        devices = [
            BoboDevice(
                addr="127.0.0.1",
                port=8086,
                urn="urn:dist:2",
                id_key="1111111111")
        ]

        decider, dec_sub = tc_decider_sub([tc_phenomenon()])

        with pytest.raises(BoboDistributedError):
            BoboDistributedTCP(
                urn="urn:dist:1",
                decider=decider,
                devices=devices,
                crypto=BoboDistributedCryptoAES("1234567890ABCDEF")
            )

    def test_multiple_devices_listed_none_are_this_device(self):
        logging.getLogger().setLevel(logging.DEBUG)

        devices = [
            BoboDevice(
                addr="127.0.0.1",
                port=8087,
                urn="urn:dist:2",
                id_key="1111111111"),
            BoboDevice(
                addr="127.0.0.1",
                port=8087,
                urn="urn:dist:3",
                id_key="1111111111"),
            BoboDevice(
                addr="127.0.0.1",
                port=8087,
                urn="urn:dist:4",
                id_key="1111111111")
        ]

        decider, dec_sub = tc_decider_sub([tc_phenomenon()])

        with pytest.raises(BoboDistributedError):
            BoboDistributedTCP(
                urn="urn:dist:1",
                decider=decider,
                devices=devices,
                crypto=BoboDistributedCryptoAES("1234567890ABCDEF")
            )

    def test_only_self_listed_in_devices(self):
        logging.getLogger().setLevel(logging.DEBUG)

        devices = [
            BoboDevice(
                addr="127.0.0.1",
                port=8088,
                urn="urn:dist:1",
                id_key="1111111111")
        ]

        decider, dec_sub = tc_decider_sub([tc_phenomenon()])

        with pytest.raises(BoboDistributedError):
            BoboDistributedTCP(
                urn="urn:dist:1",
                decider=decider,
                devices=devices,
                crypto=BoboDistributedCryptoAES("1234567890ABCDEF")
            )

    def test_run_on_close(self):
        logging.getLogger().setLevel(logging.DEBUG)

        devices = [
            BoboDevice(
                addr="127.0.0.1",
                port=8089,
                urn="urn:dist:1",
                id_key="1111111111"),
            BoboDevice(
                addr="127.0.0.1",
                port=8089,
                urn="urn:dist:2",
                id_key="2222222222")
        ]

        decider, dec_sub = tc_decider_sub([tc_phenomenon()])

        dist = BoboDistributedTCP(
            urn="urn:dist:1",
            decider=decider,
            devices=devices,
            crypto=BoboDistributedCryptoAES("1234567890ABCDEF")
        )

        dist_sub = StubDistributedSubscriber()
        dist.subscribe(dist_sub)

        t = Thread(target=tc_run_distributed_tcp, args=[dist])
        t.start()

        sleep(1)

        dist.close()
        dist.join()
        t.join()
        assert dist.is_closed()

        with pytest.raises(BoboDistributedError):
            dist.run()

    def test_run_on_running(self):
        logging.getLogger().setLevel(logging.DEBUG)

        devices = [
            BoboDevice(
                addr="127.0.0.1",
                port=8090,
                urn="urn:dist:1",
                id_key="1111111111"),
            BoboDevice(
                addr="127.0.0.1",
                port=8090,
                urn="urn:dist:2",
                id_key="2222222222")
        ]

        decider, dec_sub = tc_decider_sub([tc_phenomenon()])

        dist = BoboDistributedTCP(
            urn="urn:dist:1",
            decider=decider,
            devices=devices,
            crypto=BoboDistributedCryptoAES("1234567890ABCDEF")
        )

        dist_sub = StubDistributedSubscriber()
        dist.subscribe(dist_sub)

        t = Thread(target=tc_run_distributed_tcp, args=[dist])
        t.start()

        sleep(1)

        with pytest.raises(BoboDistributedError):
            dist.run()

        dist.close()
        dist.join()
        t.join()
        assert dist.is_closed()

    def test_on_decider_update_closed(self):
        logging.getLogger().setLevel(logging.DEBUG)

        completed: List[BoboRunSerial] = [
            tc_run_simple(
                tc_pattern(name="pattern_completed"),
                tc_event_simple(event_id="event_id_completed"),
                run_id="run_id_completed",
                phenomenon_name="phenom_name_completed",
                block_index=1
            ).serialize()]

        halted: List[BoboRunSerial] = [
            tc_run_simple(
                tc_pattern(name="pattern_halted"),
                tc_event_simple(event_id="event_id_halted"),
                run_id="run_id_halted",
                phenomenon_name="phenom_name_halted",
                block_index=1
            ).serialize()]

        updated: List[BoboRunSerial] = [
            tc_run_simple(
                tc_pattern(name="pattern_updated"),
                tc_event_simple(event_id="event_id_updated"),
                run_id="run_id_updated",
                phenomenon_name="phenom_name_updated",
                block_index=1
            ).serialize()]

        devices = [
            BoboDevice(
                addr="127.0.0.1",
                port=8091,
                urn="urn:dist:1",
                id_key="1111111111"),
            BoboDevice(
                addr="127.0.0.1",
                port=8091,
                urn="urn:dist:2",
                id_key="2222222222")
        ]

        decider, dec_sub = tc_decider_sub([tc_phenomenon()])

        dist = BoboDistributedTCP(
            urn="urn:dist:1",
            decider=decider,
            devices=devices,
            crypto=BoboDistributedCryptoAES("1234567890ABCDEF")
        )

        dist_sub = StubDistributedSubscriber()
        dist.subscribe(dist_sub)

        t = Thread(target=tc_run_distributed_tcp, args=[dist])
        t.start()

        sleep(1)

        dist.close()
        dist.join()
        t.join()
        assert dist.is_closed()

        with pytest.raises(BoboDistributedError):
            dist.on_decider_update(
                completed=completed,
                halted=halted,
                updated=updated)

    def test_on_decider_update_not_running(self):
        logging.getLogger().setLevel(logging.DEBUG)

        completed: List[BoboRunSerial] = [
            tc_run_simple(
                tc_pattern(name="pattern_completed"),
                tc_event_simple(event_id="event_id_completed"),
                run_id="run_id_completed",
                phenomenon_name="phenom_name_completed",
                block_index=1
            ).serialize()]

        halted: List[BoboRunSerial] = [
            tc_run_simple(
                tc_pattern(name="pattern_halted"),
                tc_event_simple(event_id="event_id_halted"),
                run_id="run_id_halted",
                phenomenon_name="phenom_name_halted",
                block_index=1
            ).serialize()]

        updated: List[BoboRunSerial] = [
            tc_run_simple(
                tc_pattern(name="pattern_updated"),
                tc_event_simple(event_id="event_id_updated"),
                run_id="run_id_updated",
                phenomenon_name="phenom_name_updated",
                block_index=1
            ).serialize()]

        devices = [
            BoboDevice(
                addr="127.0.0.1",
                port=8092,
                urn="urn:dist:1",
                id_key="1111111111"),
            BoboDevice(
                addr="127.0.0.1",
                port=8092,
                urn="urn:dist:2",
                id_key="2222222222")
        ]

        decider, dec_sub = tc_decider_sub([tc_phenomenon()])

        dist = BoboDistributedTCP(
            urn="urn:dist:1",
            decider=decider,
            devices=devices,
            crypto=BoboDistributedCryptoAES("1234567890ABCDEF")
        )

        with pytest.raises(BoboDistributedError):
            dist.on_decider_update(
                completed=completed,
                halted=halted,
                updated=updated)

    # TODO "Outgoing queue is full."

    # TODO resync FAILURE
    # TODO ping FAILURE
    # TODO sync FAILURE

    # TODO Check if URN is NOT a recognised device
    # TODO Check if ID key DOES NOT MATCH expected key for URN
