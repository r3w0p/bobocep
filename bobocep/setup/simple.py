# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Simple setup.
"""

from multiprocessing import cpu_count
from typing import List, Optional

from bobocep.cep.action.handler import BoboActionHandler, BoboActionHandlerPool
from bobocep.cep.engine.decider.decider import BoboDecider
from bobocep.cep.engine.engine import BoboEngine
from bobocep.cep.engine.forwarder.forwarder import BoboForwarder
from bobocep.cep.engine.producer.producer import BoboProducer
from bobocep.cep.engine.receiver.receiver import BoboReceiver
from bobocep.cep.engine.receiver.validator import BoboValidator, \
    BoboValidatorAll
from bobocep.cep.gen.event import BoboGenEvent
from bobocep.cep.gen.event_id import BoboGenEventID, BoboGenEventIDUnique
from bobocep.cep.gen.timestamp import BoboGenTimestamp, BoboGenTimestampEpoch
from bobocep.cep.phenomenon import BoboPhenomenon
from bobocep.setup.setup import BoboSetup


# TODO BoboSetupSimpleDistributed, extends BoboSetupSimple
# TODO if distributed, ensure validator is (instance of) JSONableVal


class BoboSetupSimple(BoboSetup):
    """A simple setup to make configuration easier."""

    def __init__(self,
                 phenomena: List[BoboPhenomenon],
                 validator: Optional[BoboValidator] = None,
                 handler: Optional[BoboActionHandler] = None,
                 gen_event_id: Optional[BoboGenEventID] = None,
                 gen_run_id: Optional[BoboGenEventID] = None,
                 gen_timestamp: Optional[BoboGenTimestamp] = None,
                 gen_event: Optional[BoboGenEvent] = None,
                 times_receiver: int = 0,
                 times_decider: int = 0,
                 times_producer: int = 0,
                 times_forwarder: int = 0,
                 early_stop: bool = True,
                 max_size: int = 0):
        super().__init__()

        self._max_size: int = max(0, max_size)

        self._phenomena: List[BoboPhenomenon] = phenomena
        self._validator: BoboValidator = validator \
            if validator is not None else BoboValidatorAll()
        self._handler: BoboActionHandler = handler if handler is not None \
            else BoboActionHandlerPool(processes=max(1, cpu_count() - 1),
                                       max_size=self._max_size)
        self._gen_event_id: BoboGenEventID = gen_event_id \
            if gen_event_id is not None else BoboGenEventIDUnique()
        self._gen_run_id: BoboGenEventID = gen_run_id \
            if gen_run_id is not None else BoboGenEventIDUnique()
        self._gen_timestamp: BoboGenTimestamp = gen_timestamp \
            if gen_timestamp is not None else BoboGenTimestampEpoch()
        self._gen_event: Optional[BoboGenEvent] = gen_event

        self._times_receiver: int = times_receiver
        self._times_decider: int = times_decider
        self._times_producer: int = times_producer
        self._times_forwarder: int = times_forwarder
        self._early_stop: bool = early_stop

    def generate(self) -> BoboEngine:
        receiver = BoboReceiver(
            validator=self._validator,
            gen_event=self._gen_event,
            gen_event_id=self._gen_event_id,
            gen_timestamp=self._gen_timestamp,
            max_size=self._max_size)

        decider = BoboDecider(
            phenomena=self._phenomena,
            gen_event_id=self._gen_event_id,
            gen_run_id=self._gen_run_id,
            max_size=self._max_size)

        producer = BoboProducer(
            phenomena=self._phenomena,
            gen_event_id=self._gen_event_id,
            gen_timestamp=self._gen_timestamp,
            max_size=self._max_size)

        forwarder = BoboForwarder(
            phenomena=self._phenomena,
            handler=self._handler,
            gen_event_id=self._gen_event_id,
            max_size=self._max_size)

        engine = BoboEngine(
            receiver=receiver,
            decider=decider,
            producer=producer,
            forwarder=forwarder,
            times_receiver=self._times_receiver,
            times_decider=self._times_decider,
            times_producer=self._times_producer,
            times_forwarder=self._times_forwarder,
            early_stop=self._early_stop)

        return engine
