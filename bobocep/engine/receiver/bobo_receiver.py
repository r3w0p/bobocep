from datetime import datetime
from queue import Queue, Empty, Full
from threading import RLock

from bobocep.engine.bobo_engine_task import BoboEngineTask
from bobocep.engine.receiver.bobo_receiver_publisher import \
    BoboReceiverPublisher
from bobocep.engine.receiver.exceptions.bobo_receiver_queue_full_error import \
    BoboReceiverQueueFullError
from bobocep.engine.receiver.generator.event_id.bobo_event_id import \
    BoboEventID
from bobocep.engine.receiver.generator.null_event.bobo_null_event import \
    BoboNullEvent
from bobocep.engine.receiver.validator.bobo_validator import BoboValidator
from bobocep.events.bobo_event import BoboEvent
from bobocep.events.bobo_event_primitive import BoboEventPrimitive


class BoboReceiver(BoboEngineTask, BoboReceiverPublisher):
    _STR_EXC_QUEUE_FULL = "Data queue is full (max size: {})"

    def __init__(self,
                 validator: BoboValidator,
                 event_id_gen: BoboEventID,
                 null_event_gen: BoboNullEvent,
                 max_size: int):
        super().__init__()

        self._validator = validator
        self._event_id_gen = event_id_gen
        self._null_event_gen = null_event_gen
        self._max_size = max_size
        self._queue = Queue(maxsize=self._max_size)
        self._lock = RLock()

    def update(self) -> None:
        with self._lock:
            if not self._queue.empty():
                try:
                    self._process_entity(entity=self._queue.get_nowait())
                except Empty:
                    pass

            null_event = self._null_event_gen.maybe_generate(
                event_id=self._event_id_gen.generate())

            if null_event is not None:
                self._process_entity(entity=null_event)

    def _process_entity(self, entity) -> None:
        if self._validator.is_valid(entity):
            if isinstance(entity, BoboEvent):
                event = entity
            else:
                event = BoboEventPrimitive(
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
                        self._STR_EXC_QUEUE_FULL.format(self._max_size))
            else:
                raise BoboReceiverQueueFullError(
                    self._STR_EXC_QUEUE_FULL.format(self._max_size))

    def size(self) -> int:
        with self._lock:
            return self._queue.qsize()
