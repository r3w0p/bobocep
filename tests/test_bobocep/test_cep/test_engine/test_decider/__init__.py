# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from typing import Optional, List

from bobocep.cep.engine.decider.decider import BoboDecider
from bobocep.cep.engine.decider.pubsub import BoboDeciderSubscriber
from bobocep.cep.engine.decider.run import BoboRun
from bobocep.cep.engine.decider.runserial import BoboRunSerial
from bobocep.cep.event import BoboEvent, BoboHistory
from bobocep.cep.gen.event_id import BoboGenEventID, BoboGenEventIDUnique
from bobocep.cep.phenomenon.pattern.pattern import BoboPattern
from bobocep.cep.phenomenon.phenomenon import BoboPhenomenon
from tests.test_bobocep.test_cep.test_event import tc_event_simple


class StubDeciderSubscriber(BoboDeciderSubscriber):
    def __init__(self):
        super().__init__()
        self.completed: List[BoboRunSerial] = []
        self.halted: List[BoboRunSerial] = []
        self.updated: List[BoboRunSerial] = []

    def on_decider_update(self,
                          completed: List[BoboRunSerial],
                          halted: List[BoboRunSerial],
                          updated: List[BoboRunSerial]):
        self.completed += completed
        self.halted += halted
        self.updated += updated


def tc_decider_sub(phenomena: List[BoboPhenomenon],
                   event_id_gen: Optional[BoboGenEventID] = None,
                   run_id_gen: Optional[BoboGenEventID] = None,
                   max_cache: int = 0,
                   max_size: int = 255):
    decider = BoboDecider(
        phenomena=phenomena,
        gen_event_id=event_id_gen if event_id_gen is not None else
        BoboGenEventIDUnique(),
        gen_run_id=run_id_gen if run_id_gen is not None else
        BoboGenEventIDUnique(),
        max_cache=max_cache,
        max_size=max_size)

    subscriber = StubDeciderSubscriber()
    decider.subscribe(subscriber=subscriber)

    return decider, subscriber


def tc_run_simple(
        pattern: BoboPattern,
        event: BoboEvent,
        run_id: str = "run_id",
        phenomenon_name: str = "phenomenon",
        block_index: int = 1,
        history: Optional[BoboHistory] = None):
    return BoboRun(
        run_id=run_id,
        phenomenon_name=phenomenon_name,
        pattern=pattern,
        block_index=block_index,
        history=history if history is not None else BoboHistory({
            pattern.blocks[0].group: [event]
        })
    )


def tc_run_tuple(
        run_id: str = "run_id",
        phenomenon_name: str = "phenomenon_name",
        pattern_name: str = "pattern_name",
        block_index: int = 1,
        history: Optional[BoboHistory] = None):
    return BoboRunSerial(
        run_id=run_id,
        phenomenon_name=phenomenon_name,
        pattern_name=pattern_name,
        block_index=block_index,
        history=history if history is not None else BoboHistory({
            "pattern_group": [tc_event_simple()]
        })
    )
