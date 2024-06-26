# Copyright (c) 2019-2024 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Engine task that generates complex events and triggers actions.
"""

from queue import Queue
from threading import RLock
from typing import List, Dict, Tuple

from bobocep.cep.engine.decider.pubsub import BoboDeciderSubscriber
from bobocep.cep.engine.decider.runserial import BoboRunSerial
from bobocep.cep.engine.producer.pubsub import BoboProducerPublisher, \
    BoboProducerSubscriber
from bobocep.cep.engine.task import BoboEngineTaskError, BoboEngineTask
from bobocep.cep.event import BoboEventComplex
from bobocep.cep.gen.event_id import BoboGenEventID
from bobocep.cep.gen.timestamp import BoboGenTimestamp
from bobocep.cep.phenom.phenom import BoboPhenomenon

_EXC_PHENOM_NAME_DUP = "duplicate name in phenomena: {}"
_EXC_QUEUE_FULL = "queue is full (max size: {})"


class BoboProducerError(BoboEngineTaskError):
    """
    A producer task error.
    """


class BoboProducer(BoboEngineTask,
                   BoboProducerPublisher,
                   BoboDeciderSubscriber):
    """
    A producer task.
    """

    def __init__(self,
                 phenomena: List[BoboPhenomenon],
                 gen_event_id: BoboGenEventID,
                 gen_timestamp: BoboGenTimestamp,
                 max_size: int = 0):
        """
        :param phenomena: List of phenomena.
        :param gen_event_id: Event ID generator.
        :param gen_timestamp: Timestamp generator.
        :param max_size: Maximum queue size.
            Default: 0 (unbounded).
        """
        super().__init__()
        self._lock: RLock = RLock()
        self._closed: bool = False
        self._subscribers: List[BoboProducerSubscriber] = []

        self._phenomena: Dict[str, BoboPhenomenon] = {}

        for phenom in phenomena:
            if phenom.name not in self._phenomena:
                self._phenomena[phenom.name] = phenom
            else:
                raise BoboProducerError(
                    _EXC_PHENOM_NAME_DUP.format(phenom.name))

        self._gen_event_id: BoboGenEventID = gen_event_id
        self._gen_timestamp: BoboGenTimestamp = gen_timestamp
        self._max_size: int = max(0, max_size)
        self._queue: Queue[Tuple[BoboRunSerial, bool]] = Queue(self._max_size)

    def subscribe(self, subscriber: BoboProducerSubscriber):
        """
        :param subscriber: Subscriber to Producer data.
        """
        with self._lock:
            if subscriber not in self._subscribers:
                self._subscribers.append(subscriber)

    def update(self) -> bool:
        """
        :return: `True` if an internal update occurred; `False` otherwise.
        """
        with self._lock:
            if self._closed:
                return False

            if not self._queue.empty():
                event, local = self._queue.get_nowait()
                self._handle_completed_run(event, local)
                return True

            return False

    def close(self) -> None:
        """
        Closes the Producer.
        """
        with self._lock:
            self._closed = True

    def is_closed(self) -> bool:
        """
        :return: `True` if Producer is closed; `False` otherwise.
        """
        with self._lock:
            return self._closed

    def _handle_completed_run(
            self,
            runserial: BoboRunSerial,
            local: bool
    ) -> None:
        """
        :param runserial: The run to handle.
        :param local: `True` if the run was completed locally;
            `False` if the run was completed on a
            remote (distributed) instance.
        """
        if runserial.phenomenon_name not in self._phenomena:
            raise BoboProducerError(runserial.phenomenon_name)

        phenom: BoboPhenomenon = self._phenomena[runserial.phenomenon_name]

        event_complex = BoboEventComplex(
            event_id=self._gen_event_id.generate(),
            timestamp=self._gen_timestamp.generate(),
            data=phenom.datagen(phenom, runserial.history)
            if phenom.datagen is not None else None,
            phenomenon_name=runserial.phenomenon_name,
            pattern_name=runserial.pattern_name,
            history=runserial.history)

        for subscriber in self._subscribers:
            subscriber.on_producer_update(event=event_complex, local=local)

    def on_decider_update(
            self,
            completed: List[BoboRunSerial],
            halted: List[BoboRunSerial],
            updated: List[BoboRunSerial],
            local: bool
    ) -> None:
        """
        :param completed: Completed runs.
        :param halted: Halted runs.
        :param updated: Updated runs.
        :param local: `True` if the Decider update occurred locally;
            `False` if the update occurred on a remote (distributed) instance.
        """
        with self._lock:
            if self._closed:
                return

            for run in completed:
                if not self._queue.full():
                    self._queue.put((run, local))
                else:
                    raise BoboProducerError(
                        _EXC_QUEUE_FULL.format(self._max_size))

    def size(self) -> int:
        """
        :return: Queue size.
        """
        with self._lock:
            return self._queue.qsize()
