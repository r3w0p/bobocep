# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from bobocep.engine.bobo_engine_error import BoboEngineError
from bobocep.engine.decider.bobo_decider import BoboDecider
from bobocep.engine.forwarder.bobo_forwarder import BoboForwarder
from bobocep.engine.producer.bobo_producer import BoboProducer
from bobocep.engine.receiver.bobo_receiver import BoboReceiver


class BoboEngine:
    _EXC_TIMES_REC = "'times_receiver' must be greater than or equal to 0"
    _EXC_TIMES_DEC = "'times_decider' must be greater than or equal to 0"
    _EXC_TIMES_PRO = "'times_producer' must be greater than or equal to 0"
    _EXC_TIMES_FOR = "'times_forwarder' must be greater than or equal to 0"

    def __init__(self,
                 receiver: BoboReceiver,
                 decider: BoboDecider,
                 producer: BoboProducer,
                 forwarder: BoboForwarder):
        super().__init__()

        receiver.subscribe(decider)
        decider.subscribe(producer)
        producer.subscribe(forwarder)
        producer.subscribe(receiver)
        forwarder.subscribe(receiver)

        self.receiver = receiver
        self.decider = decider
        self.producer = producer
        self.forwarder = forwarder

    def update(self,
               times_receiver: int = 0,
               times_decider: int = 0,
               times_producer: int = 0,
               times_forwarder: int = 0,
               early_stop: bool = True):

        if times_receiver < 0:
            raise BoboEngineError(self._EXC_TIMES_REC)

        if times_decider < 0:
            raise BoboEngineError(self._EXC_TIMES_DEC)

        if times_producer < 0:
            raise BoboEngineError(self._EXC_TIMES_PRO)

        if times_forwarder < 0:
            raise BoboEngineError(self._EXC_TIMES_FOR)

        for task, times in [
            (self.receiver, times_receiver),
            (self.decider, times_decider),
            (self.producer, times_producer),
            (self.forwarder, times_forwarder)
        ]:
            if times == 0:
                while task.update():
                    pass
            else:
                for i in range(times):
                    if not task.update() and early_stop:
                        break
