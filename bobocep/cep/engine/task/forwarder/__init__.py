# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""Engine task that forwards actions to external sources and generates
action events."""

from queue import Queue
from threading import RLock
from typing import Dict, List, Optional

from bobocep.cep.action.handler import BoboActionHandler
from bobocep.cep.engine.task import BoboEngineTaskError, BoboEngineTask
from bobocep.cep.engine.task.forwarder.pubsub import BoboForwarderPublisher
from bobocep.cep.engine.task.producer.pubsub import BoboProducerSubscriber
from bobocep.cep.event import BoboEventAction, BoboEventComplex
from bobocep.cep.gen.event_id import BoboGenEventID
from bobocep.cep.phenomenon import BoboPhenomenon


class BoboForwarderError(BoboEngineTaskError):
    """A forwarder task error."""


class BoboForwarder(BoboEngineTask,
                    BoboForwarderPublisher,
                    BoboProducerSubscriber):
    """A forwarder task."""

    _EXC_PHENOM_NAME_DUP = "duplicate name in phenomena: {}"
    _EXC_QUEUE_FULL = "queue is full (max size: {})"

    def __init__(self,
                 phenomena: List[BoboPhenomenon],
                 handler: BoboActionHandler,
                 gen_event_id: BoboGenEventID,
                 max_size: int = 0):
        super().__init__()

        self._lock: RLock = RLock()
        self._closed: bool = False

        self._phenomena: Dict[str, BoboPhenomenon] = {}

        for phenom in phenomena:
            if phenom.name not in self._phenomena:
                self._phenomena[phenom.name] = phenom
            else:
                raise BoboForwarderError(
                    self._EXC_PHENOM_NAME_DUP.format(phenom.name))

        self._handler: BoboActionHandler = handler
        self._gen_event_id: BoboGenEventID = gen_event_id
        self._max_size: int = max(0, max_size)
        self._queue: Queue[BoboEventComplex] = Queue(self._max_size)

    def update(self) -> bool:
        with self._lock:
            if self._closed:
                return False

            handle = self._update_handler()
            response = self._update_responses()
            return handle or response

    def close(self) -> None:
        with self._lock:
            self._closed = True

    def is_closed(self) -> bool:
        with self._lock:
            return self._closed

    def _update_handler(self) -> bool:
        if not self._queue.empty():
            event: BoboEventComplex = self._queue.get_nowait()

            if event.phenomenon_name in self._phenomena:
                phenom: BoboPhenomenon = \
                    self._phenomena[event.phenomenon_name]

                if phenom.action is not None:
                    self._handler.handle(
                        action=phenom.action,
                        event=event)
            return True
        return False

    def _update_responses(self) -> bool:
        event: Optional[BoboEventAction] = \
            self._handler.get_action_event()

        if event is not None:
            for subscriber in self._subscribers:
                subscriber.on_forwarder_update(event)
            return True
        return False

    def on_producer_update(self, event: BoboEventComplex) -> None:
        with self._lock:
            if self._closed:
                return

            if not self._queue.full():
                self._queue.put(event)
            else:
                raise BoboForwarderError(
                    self._EXC_QUEUE_FULL.format(self._max_size))

    def size(self) -> int:
        with self._lock:
            return self._queue.qsize()
