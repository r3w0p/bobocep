# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from datetime import datetime
from queue import Queue
from threading import RLock
from typing import Any

from bobocep.engine.bobo_engine_task import BoboEngineTask
from bobocep.engine.forwarder.bobo_forwarder_subscriber import \
    BoboForwarderSubscriber
from bobocep.engine.producer.bobo_producer_subscriber import \
    BoboProducerSubscriber
from bobocep.engine.receiver.bobo_receiver_error import BoboReceiverError
from bobocep.engine.receiver.bobo_receiver_publisher import \
    BoboReceiverPublisher
from bobocep.engine.receiver.event_gen.bobo_event_gen import \
    BoboEventGen
from bobocep.engine.receiver.validator.bobo_validator import BoboValidator
from bobocep.event.bobo_event import BoboEvent
from bobocep.event.bobo_event_action import BoboEventAction
from bobocep.event.bobo_event_complex import BoboEventComplex
from bobocep.event.bobo_event_simple import BoboEventSimple
from bobocep.event.event_id.bobo_event_id import BoboEventID


class BoboReceiver(BoboEngineTask,
                   BoboReceiverPublisher,
                   BoboProducerSubscriber,
                   BoboForwarderSubscriber):
    """A receiver task."""

    _EXC_QUEUE_FULL = "queue is full (max size: {})"

    def __init__(self,
                 validator: BoboValidator,
                 event_id_gen: BoboEventID,
                 event_gen: BoboEventGen,
                 max_size: int):
        super().__init__()

        self._validator = validator
        self._event_id_gen = event_id_gen
        self._event_gen = event_gen
        self._max_size = max_size
        self._queue: Queue[Any] = Queue(self._max_size)
        self._closed = False
        self._lock: RLock = RLock()

    def update(self) -> bool:
        with self._lock:
            if self._closed:
                return False

            entity = None
            if not self._queue.empty():
                entity = self._queue.get_nowait()
                self._process_entity(entity)

            gen_event = self._event_gen.maybe_generate(
                event_id=self._event_id_gen.generate())

            if gen_event is not None:
                self._process_entity(gen_event)

            return entity is not None or gen_event is not None

    def close(self) -> None:
        with self._lock:
            self._closed = True

    def is_closed(self) -> bool:
        with self._lock:
            return self._closed

    def _process_entity(self, entity: Any) -> None:
        if not self._validator.is_valid(entity):
            return None

        if isinstance(entity, BoboEvent):
            event = entity
        else:
            event = BoboEventSimple(
                event_id=self._event_id_gen.generate(),
                timestamp=datetime.now(),
                data=entity)

        for subscriber in self._subscribers:
            subscriber.on_receiver_event(event=event)

    def on_producer_complex_event(self, event: BoboEventComplex):
        with self._lock:
            if self._closed:
                return

            self.add_data(event)

    def on_forwarder_action_event(self, event: BoboEventAction):
        with self._lock:
            if self._closed:
                return

            self.add_data(event)

    def add_data(self, data: Any):
        with self._lock:
            if self._closed:
                return

            if not self._queue.full():
                self._queue.put(data)
            else:
                raise BoboReceiverError(
                    self._EXC_QUEUE_FULL.format(self._max_size))

    def size(self) -> int:
        with self._lock:
            return self._queue.qsize()
