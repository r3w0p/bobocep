from queue import Queue
from typing import List

from bobocep.decider.decider_subscriber import IDeciderSubscriber
from bobocep.decider.handlers.bobo_nfa_handler import BoboNFAHandler
from bobocep.decider.handlers.nfa_handler_subscriber import \
    INFAHandlerSubscriber
from bobocep.producer.producer_subscriber import IProducerSubscriber
from bobocep.receiver.receiver_subscriber import IReceiverSubscriber
from bobocep.rules.events.action_event import ActionEvent
from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.setup.distributed.incoming.dist_incoming_subscriber import \
    IDistIncomingSubscriber
from bobocep.setup.task.bobo_task import BoboTask


class BoboDecider(BoboTask,
                  IReceiverSubscriber,
                  IProducerSubscriber,
                  INFAHandlerSubscriber,
                  IDistIncomingSubscriber):
    """A :code:`bobocep` data decider.

    :param max_queue_size: The maximum data queue size,
                           defaults to 0 (infinite).
    :type max_queue_size: int, optional

    :param active: Whether task should start in an active state,
                   defaults to True.
    :type active: bool, optional
    """

    def __init__(self,
                 recursive: bool = True,
                 max_queue_size: int = 0,
                 active: bool = True) -> None:
        super().__init__(active=active)

        self._recursive = recursive
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
            if not self._is_cancelled:
                if nfa_handler.nfa.name not in self._nfa_handlers:
                    self._nfa_handlers[nfa_handler.nfa.name] = nfa_handler
                    nfa_handler.subscribe(self)
                else:
                    raise RuntimeError("NFA handler name {} already in use."
                                       .format(nfa_handler.nfa.name))

    def get_all_handlers(self) -> List[BoboNFAHandler]:
        """
        :return: A list of all handlers.
        """

        with self._lock:
            return list(self._nfa_handlers.values())

    def get_handler(self, name: str) -> BoboNFAHandler:
        """
        :param name: The handler name.
        :type name: str

        :return: The handler, or None if not found.
        """

        with self._lock:
            return self._nfa_handlers.get(name)

    def is_recursive(self) -> bool:
        return self._recursive

    def on_receiver_event(self, event: BoboEvent) -> None:
        if not self._is_cancelled:
            self._event_queue.put_nowait(event)

    def on_accepted_producer_event(self, event: CompositeEvent) -> None:
        if (not self._is_cancelled) and self._recursive:
            self._event_queue.put_nowait(event)

    def on_producer_action(self, event: ActionEvent):
        if (not self._is_cancelled) and \
                self._recursive and \
                isinstance(event.for_event, CompositeEvent):

            # event added to handler's recent events
            if event.for_event.name in self._nfa_handlers:
                self._nfa_handlers[event.for_event.name].add_recent(event)

            # event added to decider queue
            self._event_queue.put_nowait(event)

    def on_handler_final(self,
                         nfa_name: str,
                         run_id: str,
                         event: CompositeEvent):
        # notify producer on a new complex event being identified
        with self._lock:
            if nfa_name in self._nfa_handlers:
                if self._recursive:
                    self._nfa_handlers[nfa_name].add_recent(event)

                if nfa_name in self._subs:
                    for sub in self._subs[nfa_name]:
                        sub.on_decider_complex_event(event=event)

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
            if not self._is_cancelled:
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
            if not self._is_cancelled:
                if unsubscriber in self._subs[nfa_name]:
                    self._subs[nfa_name].remove(unsubscriber)

    def on_dist_run_transition(self,
                               nfa_name: str,
                               run_id: str,
                               state_name_from: str,
                               state_name_to: str,
                               event: BoboEvent):
        with self._lock:
            handler = self._nfa_handlers.get(nfa_name)

            if handler is None:
                raise RuntimeError(
                    "Handler not found for NFA {}.".format(nfa_name))

            handler.force_run_transition(
                run_id=run_id,
                state_name_from=state_name_from,
                state_name_to=state_name_to,
                event=event)

    def on_dist_run_clone(self,
                          nfa_name: str,
                          run_id: str,
                          next_state_name: str,
                          next_event: BoboEvent):
        with self._lock:
            handler = self._nfa_handlers.get(nfa_name)

            if handler is None:
                raise RuntimeError(
                    "Handler not found for NFA {}.".format(nfa_name))

            handler.force_run_clone(
                state_name=next_state_name,
                event=next_event,
                parent_run_id=run_id
            )

    def on_dist_run_halt(self,
                         nfa_name: str,
                         run_id: str):
        with self._lock:
            handler = self._nfa_handlers.get(nfa_name)

            if handler is None:
                raise RuntimeError(
                    "Handler not found for NFA {}.".format(nfa_name))

            handler.force_run_halt(
                run_id=run_id)

    def on_dist_run_final(self,
                          nfa_name: str,
                          run_id: str,
                          history: BoboHistory) -> None:
        with self._lock:
            handler = self._nfa_handlers.get(nfa_name)

            if handler is None:
                raise RuntimeError(
                    "Handler not found for NFA {}.".format(nfa_name))

            handler.force_run_final(
                run_id=run_id,
                history=history)

    def on_dist_action(self, event: ActionEvent) -> None:
        with self._lock:
            if isinstance(event.for_event, CompositeEvent):
                handler = self._nfa_handlers.get(event.for_event.name)

                if handler is None:
                    raise RuntimeError("Handler not found for NFA {}.".format(
                        event.for_event.name))

                handler.add_recent(event)

    def _setup(self) -> None:
        """"""

    def _cancel(self) -> None:
        """"""

    def on_invalid_data(self, data):
        """"""

    def on_rejected_producer_event(self, event: CompositeEvent):
        """"""

    def on_handler_transition(self,
                              nfa_name: str,
                              run_id: str,
                              state_name_from: str,
                              state_name_to: str,
                              event: BoboEvent):
        """"""

    def on_handler_clone(self,
                         nfa_name: str,
                         run_id: str,
                         state_name: str,
                         event: BoboEvent):
        """"""

    def on_handler_halt(self,
                        nfa_name: str,
                        run_id: str):
        """"""
