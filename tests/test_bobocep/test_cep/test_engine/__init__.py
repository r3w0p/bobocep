# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from typing import List, Optional

from bobocep.cep.action.handler import BoboActionHandler
from bobocep.cep.engine.engine import BoboEngine
from bobocep.cep.engine.receiver.validator import BoboValidator
from bobocep.cep.gen.event import BoboGenEvent
from bobocep.cep.gen.event_id import BoboGenEventID
from bobocep.cep.phenom.phenom import BoboPhenomenon
from tests.test_bobocep.test_cep.test_engine.test_decider import tc_decider_sub
from tests.test_bobocep.test_cep.test_engine.test_forwarder import \
    tc_forwarder_sub
from tests.test_bobocep.test_cep.test_engine.test_producer import \
    tc_producer_sub
from tests.test_bobocep.test_cep.test_engine.test_receiver import \
    tc_receiver_sub


def tc_engine_subs(
        phenomena: List[BoboPhenomenon],
        validator: Optional[BoboValidator] = None,
        event_id_gen: Optional[BoboGenEventID] = None,
        event_gen: Optional[BoboGenEvent] = None,
        run_id_gen: Optional[BoboGenEventID] = None,
        handler: Optional[BoboActionHandler] = None,
        times_receiver: int = 0,
        times_decider: int = 0,
        times_producer: int = 0,
        times_forwarder: int = 0,
        early_stop: bool = True,
        max_size: int = 255):
    rec, rec_sub = tc_receiver_sub(
        validator=validator,
        event_id_gen=event_id_gen,
        event_gen=event_gen,
        max_size=max_size)

    dec, dec_sub = tc_decider_sub(
        phenomena=phenomena,
        event_id_gen=event_id_gen,
        run_id_gen=run_id_gen,
        max_size=max_size)

    pro, pro_sub = tc_producer_sub(
        phenomena=phenomena,
        event_id_gen=event_id_gen,
        max_size=max_size)

    fwd, fwd_sub = tc_forwarder_sub(
        phenomena=phenomena,
        handler=handler,
        event_id_gen=event_id_gen,
        max_size=max_size)

    engine = BoboEngine(
        receiver=rec,
        decider=dec,
        producer=pro,
        forwarder=fwd,
        times_receiver=times_receiver,
        times_decider=times_decider,
        times_producer=times_producer,
        times_forwarder=times_forwarder,
        early_stop=early_stop)

    return engine, rec_sub, dec_sub, pro_sub, fwd_sub


def tc_run_engine(engine: BoboEngine):
    engine.run()
