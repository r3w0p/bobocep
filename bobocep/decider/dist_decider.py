from bobocep.decider.bobo_decider import BoboDecider
from bobocep.decider.bobo_decider_builder import BoboDeciderBuilder
from bobocep.decider.handlers.bobo_nfa_handler import BoboNFAHandler
from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.setup.distributed.incoming.dist_incoming_subscriber import \
    IDistIncomingSubscriber
from bobocep.setup.distributed.outgoing.dist_outgoing_subscriber import \
    IDistOutgoingSubscriber


class DistDecider(BoboDecider,
                  IDistIncomingSubscriber,
                  IDistOutgoingSubscriber):
    """A distributed data decider that enables synchronisation of Decider
    state across multiple instances of :code:`bobocep`.

    :param max_queue_size: The maximum data queue size,
                           defaults to 0 (infinite).
    :type max_queue_size: int, optional
    """

    def __init__(self, max_queue_size: int = 0) -> None:
        super().__init__(max_queue_size=max_queue_size)

        self.is_synced = False

    def _loop(self) -> None:
        if self.is_synced:
            super()._loop()

    def on_sync(self) -> None:
        self.is_synced = True

    def on_receiver_event(self, event: BoboEvent) -> None:
        if self.is_synced:
            super().on_receiver_event(event)

    def on_accepted_producer_event(self, event: CompositeEvent) -> None:
        if self.is_synced:
            super().on_accepted_producer_event(event)

    def get_current_state(self) -> dict:
        """
        :return: The current state of the DistDecider instance, represented as
                 a dict.
        """

        return super().to_dict()

    def put_current_state(self, new_current_state: dict) -> None:
        """
        Updates the current state of the DistDecider instance with a new
        current state, represented as a dict.

        :param new_current_state: The new current state.
        :type new_current_state: dict
        """

        if self.is_synced:
            return

        with self._lock:
            for handler_dict in new_current_state[self.HANDLERS]:
                # find the corresponding nfa handler
                nfa_name = handler_dict[BoboNFAHandler.NFA_NAME]
                handler = self._nfa_handlers[nfa_name]

                # create buffer
                buffer = BoboDeciderBuilder.shared_versioned_match_buffer(
                    handler_dict[BoboNFAHandler.BUFFER])
                handler.buffer = buffer

                # overwrite existing runs
                handler.clear_runs(halt=False, notify=False)

                for run_dict in handler_dict[BoboNFAHandler.RUNS]:
                    run = BoboDeciderBuilder.run(run_dict, buffer, handler.nfa)
                    handler.add_run(run)

            self.is_synced = True

    def on_dist_run_transition(self,
                               nfa_name: str,
                               run_id: str,
                               state_name_from: str,
                               state_name_to: str,
                               event: BoboEvent):
        with self._lock:
            handler = self._nfa_handlers.get(nfa_name)

            if handler is None:
                raise RuntimeError

            handler.force_run_transition(
                run_id,
                state_name_from,
                state_name_to,
                event)

    def on_dist_run_clone(self,
                          nfa_name: str,
                          run_id: str,
                          next_state_name: str,
                          next_event: BoboEvent):
        with self._lock:
            handler = self._nfa_handlers.get(nfa_name)

            if handler is None:
                raise RuntimeError

            handler.force_run_clone(
                run_id,
                next_state_name,
                next_event)

    def on_dist_run_halt(self,
                         nfa_name: str,
                         run_id: str):
        with self._lock:
            handler = self._nfa_handlers.get(nfa_name)

            if handler is None:
                raise RuntimeError

            handler.force_run_halt(run_id)

    def on_dist_run_final(self,
                          nfa_name: str,
                          run_id: str,
                          history: BoboHistory) -> None:
        with self._lock:
            handler = self._nfa_handlers.get(nfa_name)

            if handler is None:
                raise RuntimeError

            handler.force_run_final(run_id=run_id, history=history)

    def on_sync_response(self, sync_id: str, body: str):
        """"""
