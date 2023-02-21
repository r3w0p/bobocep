# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from threading import Thread
from time import sleep
from typing import List

import tests.common as tc
from bobocep.cep.engine.task.decider import \
    BoboRunTuple
from bobocep.dist import BoboDeviceTuple
from bobocep.dist.tcp import BoboDistributedTCP


def run_distributed_tcp(dist: BoboDistributedTCP):
    dist.run()


class TestValid:

    def test_send_completed_halted_updated(self):
        completed: List[BoboRunTuple] = [
            tc.run_simple(
                tc.pattern(name="pattern_completed"),
                tc.event_simple(event_id="event_id_completed"),
                run_id="run_id_completed",
                phenomenon_name="phenom_name_completed",
                block_index=1
            ).to_tuple()]

        halted: List[BoboRunTuple] = [
            tc.run_simple(
                tc.pattern(name="pattern_halted"),
                tc.event_simple(event_id="event_id_halted"),
                run_id="run_id_halted",
                phenomenon_name="phenom_name_halted",
                block_index=1
            ).to_tuple()]

        updated: List[BoboRunTuple] = [
            tc.run_simple(
                tc.pattern(name="pattern_updated"),
                tc.event_simple(event_id="event_id_updated"),
                run_id="run_id_updated",
                phenomenon_name="phenom_name_updated",
                block_index=1
            ).to_tuple()]

        devices = [
            BoboDeviceTuple(
                addr="127.0.0.1",
                port=8080,
                urn="urn:dist:1",
                id_key="1111111111"),
            BoboDeviceTuple(
                addr="127.0.0.1",
                port=8080,
                urn="urn:dist:2",
                id_key="2222222222")
        ]

        decider, dec_sub = tc.decider_sub([tc.phenomenon()])

        dist = BoboDistributedTCP(
            urn="urn:dist:1",
            aes_key="1234567890ABCDEF",
            decider=decider,
            devices=devices,
            subscribe=False)

        dist_sub = tc.StubDistributedSubscriber()
        dist.subscribe(dist_sub)

        t = Thread(target=run_distributed_tcp, args=[dist])
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
