# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from threading import RLock

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
                 forwarder: BoboForwarder,
                 times_receiver: int = 0,
                 times_decider: int = 0,
                 times_producer: int = 0,
                 times_forwarder: int = 0,
                 early_stop: bool = True):
        super().__init__()
        self._lock: RLock = RLock()
        self._closed: bool = False

        if times_receiver < 0:
            raise BoboEngineError(self._EXC_TIMES_REC)

        if times_decider < 0:
            raise BoboEngineError(self._EXC_TIMES_DEC)

        if times_producer < 0:
            raise BoboEngineError(self._EXC_TIMES_PRO)

        if times_forwarder < 0:
            raise BoboEngineError(self._EXC_TIMES_FOR)

        self._times_receiver: int = times_receiver
        self._times_decider: int = times_decider
        self._times_producer: int = times_producer
        self._times_forwarder: int = times_forwarder
        self._early_stop: bool = early_stop

        receiver.subscribe(decider)
        decider.subscribe(producer)
        producer.subscribe(forwarder)
        producer.subscribe(receiver)
        forwarder.subscribe(receiver)

        self.receiver: BoboReceiver = receiver
        self.decider: BoboDecider = decider
        self.producer: BoboProducer = producer
        self.forwarder: BoboForwarder = forwarder

    def close(self) -> None:
        with self._lock:
            self._closed = True

            self.receiver.close()
            self.decider.close()
            self.producer.close()
            self.forwarder.close()

    def is_closed(self) -> bool:
        with self._lock:
            return self._closed

    def run(self) -> None:
        while True:
            with self._lock:
                if self._closed:
                    return

                self.update()

    def update(self) -> bool:
        with self._lock:
            if self._closed:
                return False

            for task, times in [
                (self.receiver, self._times_receiver),
                (self.decider, self._times_decider),
                (self.producer, self._times_producer),
                (self.forwarder, self._times_forwarder)
            ]:
                if times == 0:
                    while task.update():
                        pass
                else:
                    for i in range(times):
                        if not task.update() and self._early_stop:
                            break
            # TODO pytest "return True" issue
            return not self._closed
