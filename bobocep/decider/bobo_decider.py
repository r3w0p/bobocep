from queue import Queue
from typing import List

from bobocep.decider.abstract_decider import AbstractDecider
from bobocep.decider.decider_subscriber import IDeciderSubscriber
from bobocep.decider.handlers.bobo_nfa_handler import BoboNFAHandler
from bobocep.decider.handlers.nfa_handler_subscriber import \
    INFAHandlerSubscriber
from bobocep.producer.producer_subscriber import IProducerSubscriber
from bobocep.receiver.receiver_subscriber import IReceiverSubscriber
from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.setup.task.bobo_task import BoboTask


class BoboDecider(AbstractDecider,
                  BoboTask,
                  IReceiverSubscriber,
                  INFAHandlerSubscriber,
                  IProducerSubscriber):
    """A :code:`bobocep` data decider.

    :param max_queue_size: The maximum data queue size,
                           defaults to 0 (infinite).
    :type max_queue_size: int, optional
    """

    HANDLERS = "handlers"

    def __init__(self, max_queue_size: int = 0) -> None:
        super().__init__()

        self._event_queue = Queue(maxsize=max_queue_size)
        self._nfa_handlers = {}
        self._subs = {}

    def _loop(self) -> None:
        if not self._event_queue.empty():
            event = self._event_queue.get_nowait()

            if event is not None:
                for nfa_handler in self._nfa_handlers.values():
                    nfa_handler.process(event)

    def add_nfa_handler(self, nfa_handler: BoboNFAHandler) -> None:
        """
        Adds a new NFA handler to the decider.

        :param nfa_handler: The NFA handler to add.
        :type nfa_handler: BoboNFAHandler

        :raises RuntimeError: NFA handler name already in use.
        """

        with self._lock:
            if not self._cancelled:
                if nfa_handler.nfa.name not in self._nfa_handlers:
                    self._nfa_handlers[nfa_handler.nfa.name] = nfa_handler
                    nfa_handler.subscribe(self)
                else:
                    raise RuntimeError("NFA handler name {} already in use."
                                       .format(nfa_handler.nfa.name))

    def get_handlers(self) -> List[BoboNFAHandler]:
        return list(self._nfa_handlers.values())

    def on_receiver_event(self, event: BoboEvent) -> None:
        if not self._cancelled:
            self._event_queue.put(event)

    def on_accepted_producer_event(self, event: CompositeEvent) -> None:
        if not self._cancelled:
            self._event_queue.put(event)

    def on_handler_final(self,
                         nfa_name: str,
                         run_id: str,
                         event: CompositeEvent) -> None:
        with self._lock:
            if not self._cancelled:
                self._notify_new_complex_event(
                    nfa_name=nfa_name,
                    event=event)

    def _notify_new_complex_event(self,
                                  nfa_name: str,
                                  event: CompositeEvent):
        if nfa_name in self._subs:
            for sub in self._subs[nfa_name]:
                sub.on_decider_complex_event(nfa_name=nfa_name, event=event)

    def subscribe(self,
                  nfa_name: str,
                  subscriber: IDeciderSubscriber) -> None:
        """
        :param nfa_name: The NFA to subscribe to.
        :type nfa_name: str

        :param subscriber: Subscribes to NFA in Decider.
        :type subscriber: IDeciderSubscriber

        :raises RuntimeError: NFA name not found.
        """

        with self._lock:
            if not self._cancelled:
                if nfa_name not in self._nfa_handlers:
                    raise RuntimeError("NFA name {} not found in handlers."
                                       .format(nfa_name))

                if nfa_name not in self._subs:
                    self._subs[nfa_name] = []

                if subscriber not in self._subs[nfa_name]:
                    self._subs[nfa_name].append(subscriber)

    def unsubscribe(self,
                    nfa_name: str,
                    unsubscriber: IDeciderSubscriber) -> None:
        """
        :param nfa_name: The NFA to unsubscribe from.
        :type nfa_name: str

        :param unsubscriber: Subscribes to NFA in Decider.
        :type unsubscriber: IDeciderSubscriber
        """

        with self._lock:
            if nfa_name in self._subs:
                if unsubscriber in self._subs[nfa_name]:
                    self._subs[nfa_name].remove(unsubscriber)

    def to_dict(self) -> dict:
        """
        :return: A dict representation of the object.
        """

        with self._lock:
            return {
                self.HANDLERS: [handler.to_dict() for handler in
                                self._nfa_handlers.values()]
            }

    def on_invalid_data(self, data) -> None:
        """"""

    def on_rejected_producer_event(self, event: CompositeEvent) -> None:
        """"""

    def on_handler_transition(self,
                              nfa_name: str,
                              run_id: str,
                              state_name_from: str,
                              state_name_to: str,
                              event: BoboEvent) -> None:
        """"""

    def on_handler_clone(self,
                         nfa_name: str,
                         run_id: str,
                         state_name: str,
                         event: BoboEvent) -> None:
        """"""

    def on_handler_halt(self,
                        nfa_name: str,
                        run_id: str) -> None:
        """"""

    def _setup(self) -> None:
        """"""

    def _cancel(self) -> None:
        """"""
