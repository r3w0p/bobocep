# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Engine task that provides an entry point for data into the system.
"""

from queue import Queue
from threading import RLock
from typing import Optional, Any, List

from bobocep.cep.engine.forwarder.pubsub import BoboForwarderSubscriber
from bobocep.cep.engine.producer.pubsub import BoboProducerSubscriber
from bobocep.cep.engine.receiver.pubsub import BoboReceiverPublisher, \
    BoboReceiverSubscriber
from bobocep.cep.engine.receiver.validator import BoboValidator
from bobocep.cep.engine.task import BoboEngineTaskError, BoboEngineTask
from bobocep.cep.event import BoboEvent, BoboEventSimple, BoboEventComplex, \
    BoboEventAction
from bobocep.cep.gen.event import BoboGenEvent
from bobocep.cep.gen.event_id import BoboGenEventID
from bobocep.cep.gen.timestamp import BoboGenTimestamp

_EXC_QUEUE_FULL = "queue is full (max size: {})"


class BoboReceiverError(BoboEngineTaskError):
    """
    A receiver task error.
    """


class BoboReceiver(BoboEngineTask,
                   BoboReceiverPublisher,
                   BoboProducerSubscriber,
                   BoboForwarderSubscriber):
    """
    A receiver task.
    """

    def __init__(self,
                 validator: BoboValidator,
                 gen_event_id: BoboGenEventID,
                 gen_timestamp: BoboGenTimestamp,
                 gen_event: Optional[BoboGenEvent] = None,
                 max_size: int = 0):
        """
        :param validator: Incoming data validator.
        :param gen_event_id: Event ID generator.
        :param gen_timestamp: Timestamp generator.
        :param gen_event: Event generator (optional).
        :param max_size: Maximum queue size.
            Default: 0 (unbounded).
        """
        super().__init__()

        self._lock: RLock = RLock()
        self._closed: bool = False
        self._subscribers: List[BoboReceiverSubscriber] = []

        self._validator: BoboValidator = validator
        self._gen_event_id: BoboGenEventID = gen_event_id
        self._gen_timestamp: BoboGenTimestamp = gen_timestamp
        self._gen_event: Optional[BoboGenEvent] = gen_event

        self._max_size: int = max(0, max_size)
        self._queue: Queue[Any] = Queue(self._max_size)

    def subscribe(self, subscriber: BoboReceiverSubscriber) -> None:
        """
        :param subscriber: Subscriber to Receiver data.
        """
        with self._lock:
            if subscriber not in self._subscribers:
                self._subscribers.append(subscriber)

    def add_data(self, data: Any) -> None:
        """
        :param data: Data to add to the receiver.

        :raises BoboReceiverError: If receiver queue is full.
        """
        with self._lock:
            if self._closed:
                return

            if not self._queue.full():
                self._queue.put(data)
            else:
                raise BoboReceiverError(
                    _EXC_QUEUE_FULL.format(self._max_size))

    def _process_data(self, data: Any) -> None:
        """
        :param data: Data to process.
        """
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

    def update(self) -> bool:
        """
        Processes data from its queue, if any.
        Also processes a generated event if receiver is set to generate any.
        A BoboEventSimple instance is produced for data if they pass validation
        and are not already BoboEvent instances. Valid data are then sent to
        receiver subscribers.

        :return: `True` if queue or generated data are processed;
            `False` otherwise.
        """
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

    def size(self) -> int:
        """
        :return: Queue size.
        """
        with self._lock:
            return self._queue.qsize()

    def close(self) -> None:
        """
        Closes the Receiver.
        """
        with self._lock:
            self._closed = True

    def is_closed(self) -> bool:
        """
        :return: `True` if Receiver is closed; `False` otherwise.
        """
        with self._lock:
            return self._closed

    def on_producer_update(
            self,
            event: BoboEventComplex,
            local: bool
    ) -> None:
        """
        :param event: Complex event generated by Producer.
        :param local: `True` if the complex event was generated using
            a locally-completed run; `False` otherwise.
        """
        with self._lock:
            if self._closed:
                return

            self.add_data(event)

    def on_forwarder_update(self, event: BoboEventAction) -> None:
        """
        :param event: Action event generated by Forwarder.
        """
        with self._lock:
            if self._closed:
                return

            self.add_data(event)
