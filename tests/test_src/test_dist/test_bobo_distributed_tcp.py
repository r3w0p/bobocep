# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
import json

import pytest
from threading import Thread
from src.cep.engine.decider.bobo_decider_run_tuple import \
    BoboDeciderRunTuple
from src.cep.event.bobo_history import BoboHistory
import tests.common as tc
from src.dist.bobo_device_tuple import BoboDeviceTuple
from src.dist.bobo_distributed_tcp import BoboDistributedTCP
from pprint import pprint
from time import sleep


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
                urn="urn_dist",
                id_key="1234567890"),
            BoboDeviceTuple(
                addr="127.0.0.1",
                port=8080,
                urn="urn_dist_2",
                id_key="1234567890")
        ]

        dist = BoboDistributedTCP(
            urn="urn_dist",
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

        sleep(1)

        dist.close()
        dist.join()
        t.join()

        assert dist.size_outgoing() == 0
        assert dist.size_incoming() == 1

        print(dist._queue_incoming.get_nowait())
