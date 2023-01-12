# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from threading import Thread
from time import sleep

import tests.common as tc
from bobocep.cep.engine.task.decider import \
    BoboDeciderRunTuple
from bobocep.cep.event import BoboHistory
from bobocep.dist import BoboDeviceTuple
from bobocep.dist.tcp import BoboDistributedTCP


def run_distributed_tcp(dist: BoboDistributedTCP):
    dist.run()


class TestValid:

    def test_queues_on_decider_update(self):
        halted_complete = [BoboDeciderRunTuple(
            process_name="process_hc",
            pattern_name="pattern_hc",
            block_index=1,
            history=BoboHistory(events={"group_hc": [tc.event_simple()]}))]

        halted_incomplete = [BoboDeciderRunTuple(
            process_name="process_hi",
            pattern_name="pattern_hi",
            block_index=2,
            history=BoboHistory(events={"group_hi": [tc.event_simple()]}))]

        updated = [BoboDeciderRunTuple(
            process_name="process_up",
            pattern_name="pattern_up",
            block_index=3,
            history=BoboHistory(events={"group_up": [tc.event_simple()]}))]

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

        dist = BoboDistributedTCP(
            urn="urn:dist:1",
            devices=devices,
            aes_key="1234567890ABCDEF",
            max_size_incoming=255,
            max_size_outgoing=255)

        t = Thread(target=run_distributed_tcp, args=[dist])
        t.start()

        dist.on_decider_update(
            halted_complete=halted_complete,
            halted_incomplete=halted_incomplete,
            updated=updated)

        sleep(3)

        dist.close()
        dist.join()
        t.join()

        assert dist.size_outgoing() == 0
        assert dist.size_incoming() == 1
