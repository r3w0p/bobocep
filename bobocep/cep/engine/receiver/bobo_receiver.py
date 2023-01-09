# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from queue import Queue
from threading import RLock
from typing import Any, Optional

from bobocep.cep.engine.bobo_engine_task import BoboEngineTask
from bobocep.cep.engine.forwarder.bobo_forwarder_subscriber import \
    BoboForwarderSubscriber
from bobocep.cep.engine.producer.bobo_producer_subscriber import \
    BoboProducerSubscriber
from bobocep.cep.engine.receiver.bobo_receiver_error import BoboReceiverError
from bobocep.cep.engine.receiver.bobo_receiver_publisher import \
    BoboReceiverPublisher
from bobocep.cep.gen.event.bobo_gen_event import \
    BoboGenEvent
from bobocep.cep.engine.receiver.validator.bobo_validator import BoboValidator
from bobocep.cep.event.bobo_event import BoboEvent
from bobocep.cep.event.bobo_event_action import BoboEventAction
from bobocep.cep.event.bobo_event_complex import BoboEventComplex
from bobocep.cep.event.bobo_event_simple import BoboEventSimple
from bobocep.cep.gen.event_id.bobo_gen_event_id import BoboGenEventID
from bobocep.cep.gen.timestamp.bobo_gen_timestamp import BoboGenTimestamp
from bobocep.cep.gen.timestamp.bobo_gen_timestamp_epoch import \
    BoboGenTimestampEpoch


class BoboReceiver(BoboEngineTask,
                   BoboReceiverPublisher,
                   BoboProducerSubscriber,
                   BoboForwarderSubscriber):
    """A receiver task."""

    _EXC_QUEUE_FULL = "queue is full (max size: {})"

    def __init__(self,
                 validator: BoboValidator,
                 gen_event_id: BoboGenEventID,
                 gen_timestamp: BoboGenTimestamp,
                 gen_event: Optional[BoboGenEvent],
                 max_size: int = 0):
        super().__init__()

        self._lock: RLock = RLock()
        self._closed: bool = False

        self._validator: BoboValidator = validator
        self._gen_event_id: BoboGenEventID = gen_event_id
        self._gen_timestamp: BoboGenTimestamp = gen_timestamp
        self._gen_event: Optional[BoboGenEvent] = gen_event

        self._max_size: int = max(0, max_size)
        self._queue: Queue[Any] = Queue(self._max_size)

    def update(self) -> bool:
        with self._lock:
            if self._closed:
                return False

            data: Any = None
            event_gen: Optional[BoboEvent] = None

            if not self._queue.empty():
                data = self._queue.get_nowait()
                self._process_data(data)

            if self._gen_event is not None:
                event_gen = self._gen_event.maybe_generate(
                    self._gen_event_id.generate())

                if event_gen is not None:
                    self._process_data(event_gen)

            return data is not None or event_gen is not None

    def close(self) -> None:
        with self._lock:
            self._closed = True

    def is_closed(self) -> bool:
        with self._lock:
            return self._closed

    def _process_data(self, data: Any) -> None:
        if not self._validator.is_valid(data):
            return None

        if isinstance(data, BoboEvent):
            event = data
        else:
            event = BoboEventSimple(
                event_id=self._gen_event_id.generate(),
                timestamp=self._gen_timestamp.generate(),
                data=data)

        for subscriber in self._subscribers:
            subscriber.on_receiver_update(event)

    def on_producer_update(self, event: BoboEventComplex) -> None:
        with self._lock:
            if self._closed:
                return

            self.add_data(event)

    def on_forwarder_update(self, event: BoboEventAction) -> None:
        with self._lock:
            if self._closed:
                return

            self.add_data(event)

    def add_data(self, data: Any) -> None:
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
