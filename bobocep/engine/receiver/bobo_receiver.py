# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from datetime import datetime
from queue import Queue, Full
from threading import RLock
from typing import Union

from bobocep.engine.bobo_engine_task import BoboEngineTask
from bobocep.engine.receiver.bobo_receiver_publisher import \
    BoboReceiverPublisher
from bobocep.engine.receiver.exception.bobo_receiver_queue_full_error import \
    BoboReceiverQueueFullError
from bobocep.engine.receiver.null_event.bobo_null_event import \
    BoboNullEvent
from bobocep.engine.receiver.validator.bobo_validator import BoboValidator
from bobocep.event.bobo_event import BoboEvent
from bobocep.event.bobo_event_simple import BoboEventSimple
from bobocep.event.event_id.bobo_event_id import BoboEventID


class BoboReceiver(BoboEngineTask, BoboReceiverPublisher):
    _EXC_QUEUE_FULL = "queue is full (max size: {})"

    def __init__(self,
                 validator: BoboValidator,
                 event_id_gen: BoboEventID,
                 null_event_gen: Union[BoboNullEvent, None],
                 max_size: int):
        super().__init__()

        self._validator = validator
        self._event_id_gen = event_id_gen
        self._null_event_gen = null_event_gen
        self._max_size = max_size
        self._queue: Queue = Queue(maxsize=self._max_size)
        self._lock = RLock()

    def update(self) -> None:
        with self._lock:
            if not self._queue.empty():
                self._process_entity(entity=self._queue.get_nowait())

            if self._null_event_gen is not None:
                null_event = self._null_event_gen.maybe_generate(
                    event_id=self._event_id_gen.generate())

                if null_event is not None:
                    self._process_entity(entity=null_event)

    def _process_entity(self, entity) -> None:
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

    def add_data(self, data):
        with self._lock:
            if not self._queue.full():
                try:
                    self._queue.put(data)
                except Full:
                    raise BoboReceiverQueueFullError(
                        self._EXC_QUEUE_FULL.format(self._max_size))
            else:
                raise BoboReceiverQueueFullError(
                    self._EXC_QUEUE_FULL.format(self._max_size))

    def size(self) -> int:
        with self._lock:
            return self._queue.qsize()
