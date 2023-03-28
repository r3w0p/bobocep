# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
import logging
from threading import Thread
from time import sleep
from typing import List

from bobocep.cep.engine.decider.runtup import BoboRunTuple
from bobocep.dist.crypto.aes import BoboDistributedCryptoAES
from bobocep.dist.device import BoboDevice
from bobocep.dist.tcp import BoboDistributedTCP
from tests.test_bobocep.test_cep.test_engine.test_decider import tc_run_simple, \
    tc_decider_sub
from tests.test_bobocep.test_cep.test_event import tc_event_simple
from tests.test_bobocep.test_cep.test_phenomenon import tc_pattern, \
    tc_phenomenon
from tests.test_bobocep.test_dist import StubDistributedSubscriber, \
    tc_run_distributed_tcp


# TODO test addr change


class TestValid:

    def test_send_completed_halted_updated_to_another_device_aes(self):
        logging.getLogger().setLevel(logging.DEBUG)

        completed: List[BoboRunTuple] = [
            tc_run_simple(
                tc_pattern(name="pattern_completed"),
                tc_event_simple(event_id="event_id_completed"),
                run_id="run_id_completed",
                phenomenon_name="phenom_name_completed",
                block_index=1
            ).to_tuple()]

        halted: List[BoboRunTuple] = [
            tc_run_simple(
                tc_pattern(name="pattern_halted"),
                tc_event_simple(event_id="event_id_halted"),
                run_id="run_id_halted",
                phenomenon_name="phenom_name_halted",
                block_index=1
            ).to_tuple()]

        updated: List[BoboRunTuple] = [
            tc_run_simple(
                tc_pattern(name="pattern_updated"),
                tc_event_simple(event_id="event_id_updated"),
                run_id="run_id_updated",
                phenomenon_name="phenom_name_updated",
                block_index=1
            ).to_tuple()]

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
            subscribe=False,  # to stop interference by decider
            flag_reset=False  # to prevent initial FORCE_RESYNC
        )

        dist_sub = StubDistributedSubscriber()
        dist.subscribe(dist_sub)

        # Sets Distributed to "OK Period"
        dist._devices[devices[0].urn].last_comms = BoboDistributedTCP._now()
        dist._devices[devices[1].urn].last_comms = BoboDistributedTCP._now()

        t = Thread(target=tc_run_distributed_tcp, args=[dist])
        t.start()

        sleep(1)

        dist.on_decider_update(
            completed=completed,
            halted=halted,
            updated=updated)

        sleep(1)

        dist.close()
        dist.join()
        t.join()

        assert dist.size_outgoing() == 0
        assert dist.size_incoming() == 0

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
            assert idistsub[0].history.all()[0].event_id == \
                   irun[0].history.all()[0].event_id
