# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from multiprocessing import cpu_count
from typing import List, Optional

from src.cep.action.handler.bobo_action_handler import BoboActionHandler
from src.cep.action.handler.bobo_action_handler_pool import \
    BoboActionHandlerPool
from src.cep.engine.bobo_engine import BoboEngine
from src.cep.engine.decider.bobo_decider import BoboDecider
from src.cep.engine.forwarder.bobo_forwarder import BoboForwarder
from src.cep.engine.producer.bobo_producer import BoboProducer
from src.cep.engine.receiver.bobo_receiver import BoboReceiver
from src.cep.engine.receiver.event_gen.bobo_event_gen import BoboEventGen
from src.cep.engine.receiver.event_gen.bobo_event_gen_time import \
    BoboEventGenTime
from src.cep.engine.receiver.validator.bobo_validator import BoboValidator
from src.cep.engine.receiver.validator.bobo_validator_all import \
    BoboValidatorAll
from src.cep.event.event_id_gen.bobo_event_id_gen import BoboEventIDGen
from src.cep.event.event_id_gen.bobo_event_id_gen_unique import \
    BoboEventIDGenUnique
from src.cep.process.bobo_process import BoboProcess
from src.dist.bobo_distributed import BoboDistributed
from src.setup.bobo_setup import BoboSetup


class BoboSetupSimple(BoboSetup):
    """A simple setup to make the configuration of BoboCEP easier."""

    def __init__(self,
                 processes: List[BoboProcess],
                 validator: Optional[BoboValidator] = None,
                 event_id_gen: Optional[BoboEventIDGen] = None,
                 event_gen: Optional[BoboEventGen] = None,
                 run_id_gen: Optional[BoboEventIDGen] = None,
                 handler: Optional[BoboActionHandler] = None,
                 times_receiver: int = 0,
                 times_decider: int = 0,
                 times_producer: int = 0,
                 times_forwarder: int = 0,
                 early_stop: bool = True,
                 distributed: Optional[BoboDistributed] = None,
                 max_size: int = 0):
        super().__init__()

        self._processes: List[BoboProcess] = processes

        self._validator: BoboValidator = validator \
            if validator is not None else BoboValidatorAll()
        self._event_id_gen: BoboEventIDGen = event_id_gen \
            if event_id_gen is not None else BoboEventIDGenUnique()
        self._event_gen: BoboEventGen = event_gen \
            if event_gen is not None else BoboEventGenTime(
            milliseconds=1000,
            datagen=lambda: None)
        self._run_id_gen: BoboEventIDGen = run_id_gen \
            if run_id_gen is not None else BoboEventIDGenUnique()
        self._handler: BoboActionHandler = handler \
            if handler is not None else BoboActionHandlerPool(
            max_size=max_size,
            processes=max(1, cpu_count() - 1))

        self._times_receiver: int = times_receiver
        self._times_decider: int = times_decider
        self._times_producer: int = times_producer
        self._times_forwarder: int = times_forwarder
        self._early_stop: bool = early_stop
        self._distributed: Optional[BoboDistributed] = distributed
        self._max_size: int = max_size

    def generate(self) -> BoboEngine:
        # TODO if distributed, ensure validator is instanceof JSONableVal
        receiver = BoboReceiver(
            validator=self._validator,
            event_id_gen=self._event_id_gen,
            event_gen=self._event_gen,
            max_size=self._max_size)

        decider = BoboDecider(
            processes=self._processes,
            event_id_gen=self._event_id_gen,
            run_id_gen=self._run_id_gen,
            max_size=self._max_size)

        producer = BoboProducer(
            processes=self._processes,
            event_id_gen=self._event_id_gen,
            max_size=self._max_size)

        forwarder = BoboForwarder(
            processes=self._processes,
            handler=self._handler,
            event_id_gen=self._event_id_gen,
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

        if self._distributed is not None:
            receiver.subscribe(self._distributed)
            decider.subscribe(self._distributed)
            producer.subscribe(self._distributed)
            forwarder.subscribe(self._distributed)

        return engine
