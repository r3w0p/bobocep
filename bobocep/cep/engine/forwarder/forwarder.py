# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Engine task that forwards actions to external sources and generates
action events.
"""

from queue import Queue
from threading import RLock
from typing import Dict, List, Optional

from bobocep.cep.action.handler import BoboActionHandler, BoboHandlerResponse
from bobocep.cep.engine.forwarder.pubsub import BoboForwarderPublisher, \
    BoboForwarderSubscriber
from bobocep.cep.engine.producer.pubsub import BoboProducerSubscriber
from bobocep.cep.engine.task import BoboEngineTaskError, BoboEngineTask
from bobocep.cep.event import BoboEventAction, BoboEventComplex
from bobocep.cep.gen import BoboGenTimestamp
from bobocep.cep.gen.event_id import BoboGenEventID
from bobocep.cep.phenom.phenom import BoboPhenomenon

_EXC_PHENOM_NAME_DUP = "duplicate name in phenomena: {}"
_EXC_QUEUE_FULL = "queue is full (max size: {})"


class BoboForwarderError(BoboEngineTaskError):
    """
    A forwarder task error.
    """


class BoboForwarder(BoboEngineTask,
                    BoboForwarderPublisher,
                    BoboProducerSubscriber):
    """
    A forwarder task.
    """

    def __init__(self,
                 phenomena: List[BoboPhenomenon],
                 handler: BoboActionHandler,
                 gen_event_id: BoboGenEventID,
                 gen_timestamp: BoboGenTimestamp,
                 max_size: int = 0):
        """
        :param phenomena: List of phenomena.
        :param handler: Action handler.
        :param gen_event_id: Event ID generator.
        :param gen_timestamp: Timestamp generator.
        :param max_size: Maximum queue size.
            Default: 0 (unbounded).
        """
        super().__init__()

        self._lock: RLock = RLock()
        self._closed: bool = False
        self._subscribers: List[BoboForwarderSubscriber] = []

        self._phenomena: Dict[str, BoboPhenomenon] = {}

        for phenom in phenomena:
            if phenom.name not in self._phenomena:
                self._phenomena[phenom.name] = phenom
            else:
                raise BoboForwarderError(
                    _EXC_PHENOM_NAME_DUP.format(phenom.name))

        self._handler: BoboActionHandler = handler
        self._gen_event_id: BoboGenEventID = gen_event_id
        self._gen_timestamp: BoboGenTimestamp = gen_timestamp
        self._max_size: int = max(0, max_size)
        self._queue: Queue[BoboEventComplex] = Queue(self._max_size)

    def subscribe(self, subscriber: BoboForwarderSubscriber):
        """
        :param subscriber: Subscriber to Forwarder data.
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

            handle = self._update_handler()
            response = self._update_responses()
            return handle or response

    def close(self) -> None:
        """
        Closes the Forwarder.
        """
        with self._lock:
            self._closed = True

    def is_closed(self) -> bool:
        """
        :return: `True` if Forwarder is closed; `False` otherwise.
        """
        with self._lock:
            return self._closed

    def _update_handler(self) -> bool:
        """
        :return: `True` if update occurred; `False` otherwise.
        """
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
        """
        :return: `True` if subscribers were notified of an action event
            from the action handler; `False` otherwise.
        """
        hres: Optional[BoboHandlerResponse] = \
            self._handler.get_handler_response()

        if hres is not None:
            # Generate action event from handler response
            event = BoboEventAction(
                event_id=self._gen_event_id.generate(),
                timestamp=self._gen_timestamp.generate(),
                data=hres.data,
                phenomenon_name=hres.complex_event.phenomenon_name,
                pattern_name=hres.complex_event.pattern_name,
                action_name=hres.action_name,
                success=hres.success)

            for subscriber in self._subscribers:
                subscriber.on_forwarder_update(event)

            return True

        return False

    def on_producer_update(self, event: BoboEventComplex) -> None:
        """
        :param event: Complex event generated by Producer.
        """
        with self._lock:
            if self._closed:
                return

            if not self._queue.full():
                self._queue.put(event)
            else:
                raise BoboForwarderError(
                    _EXC_QUEUE_FULL.format(self._max_size))

    def size(self) -> int:
        """
        :return: Queue size.
        """
        with self._lock:
            return self._queue.qsize()
