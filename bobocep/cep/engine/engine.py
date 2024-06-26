# Copyright (c) 2019-2024 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
CEP engine.
"""

from threading import RLock

from bobocep import BoboError
from bobocep.cep.engine.decider.decider import BoboDecider
from bobocep.cep.engine.forwarder.forwarder import BoboForwarder
from bobocep.cep.engine.producer.producer import BoboProducer
from bobocep.cep.engine.receiver.receiver import BoboReceiver

_EXC_TIMES_REC = "receiver times must be greater than or equal to 0"
_EXC_TIMES_DEC = "decider times must be greater than or equal to 0"
_EXC_TIMES_PRO = "producer times must be greater than or equal to 0"
_EXC_TIMES_FOR = "forwarder times must be greater than or equal to 0"


class BoboEngineError(BoboError):
    """
    An engine error.
    """


class BoboEngine:
    """
    The engine for complex event processing.
    """

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
        """
        :param receiver: The receiver task.
        :param decider: The decider task.
        :param producer: The producer task.
        :param forwarder: The forwarder task.
        :param times_receiver: The number of times to run the receiver until
            moving to the decider task. A value of `0` runs the receiver
            indefinitely until it no longer performs an update of its
            internal state.
        :param times_decider: The number of times to run the decider until
            moving to the producer task. A value of `0` runs the decider
            indefinitely until it no longer performs an update of its
            internal state.
        :param times_producer: The number of times to run the producer until
            moving to the forwarder task. A value of `0` runs the producer
            indefinitely until it no longer performs an update of its
            internal state.
        :param times_forwarder: The number of times to run the forwarder until
            moving to the receiver task. A value of `0` runs the forwarder
            indefinitely until it no longer performs an update of its
            internal state.
        :param early_stop: If `times_*` is greater than `0`, it will always
            run the task for the set number of times, even if the task does
            not update. Setting `early_stop` to `True` stops early if no task
            update occurs.
        """
        super().__init__()
        self._lock: RLock = RLock()
        self._closed: bool = False

        if times_receiver < 0:
            raise BoboEngineError(_EXC_TIMES_REC)

        if times_decider < 0:
            raise BoboEngineError(_EXC_TIMES_DEC)

        if times_producer < 0:
            raise BoboEngineError(_EXC_TIMES_PRO)

        if times_forwarder < 0:
            raise BoboEngineError(_EXC_TIMES_FOR)

        self._times_receiver: int = times_receiver
        self._times_decider: int = times_decider
        self._times_producer: int = times_producer
        self._times_forwarder: int = times_forwarder
        self._early_stop: bool = early_stop

        self._receiver: BoboReceiver = receiver
        self._decider: BoboDecider = decider
        self._producer: BoboProducer = producer
        self._forwarder: BoboForwarder = forwarder

        self._receiver.subscribe(decider)
        self._decider.subscribe(producer)
        self._producer.subscribe(forwarder)
        self._producer.subscribe(receiver)
        self._forwarder.subscribe(receiver)

    @property
    def receiver(self) -> BoboReceiver:
        """
        Get receiver task.
        """
        return self._receiver

    @property
    def decider(self) -> BoboDecider:
        """
        Get decider task.
        """
        return self._decider

    @property
    def producer(self) -> BoboProducer:
        """
        Get producer task.
        """
        return self._producer

    @property
    def forwarder(self) -> BoboForwarder:
        """
        Get forwarder task.
        """
        return self._forwarder

    def close(self) -> None:
        """
        Closes the engine.
        """
        with self._lock:
            self._closed = True

            self._receiver.close()
            self._decider.close()
            self._producer.close()
            self._forwarder.close()

    def is_closed(self) -> bool:
        """
        :return: `True` if engine is set to close; `False` otherwise.
        """
        with self._lock:
            return self._closed

    def run(self) -> None:
        """
        Runs the engine. This is a blocking operation.
        """
        while True:
            with self._lock:
                if self._closed:
                    return

                self.update()

    def update(self) -> bool:
        """
        Updates the receiver, then the decider, then the producer, and
        finally to the forwarder.
        It updates each task `n` times, depending on how many times were
        chosen during engine instantiation.

        :return: `True` if engine is not set to close; `False` otherwise.
        """
        with self._lock:
            if self._closed:
                return False

            for task, times in [
                (self._receiver, self._times_receiver),
                (self._decider, self._times_decider),
                (self._producer, self._times_producer),
                (self._forwarder, self._times_forwarder)
            ]:
                if times == 0:
                    while task.update():
                        pass
                else:
                    for i in range(times):
                        if not task.update() and self._early_stop:
                            break

            return not self._closed
