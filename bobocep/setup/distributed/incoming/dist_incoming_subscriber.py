from abc import ABC, abstractmethod

from bobocep.rules.events.bobo_event import BoboEvent


class IDistIncomingSubscriber(ABC):

    @abstractmethod
    def on_dist_run_transition(self,
                               nfa_name: str,
                               run_id: str,
                               state_name_from: str,
                               state_name_to: str,
                               event: BoboEvent) -> None:
        """
        When a transition has occurred on a run on another :code:`bobocep`
        instance.

        :param nfa_name: The NFA name.
        :type nfa_name: str

        :param run_id: The ID of the run that transitioned.
        :type run_id: str

        :param state_name_from: The original state.
        :type state_name_from: str

        :param state_name_to: The new state.
        :type state_name_to: str

        :param event: The event that caused the transition.
        :type event: BoboEvent
        """

    @abstractmethod
    def on_dist_run_clone(self,
                          nfa_name: str,
                          run_id: str,
                          next_state_name: str,
                          next_event: BoboEvent) -> None:
        """
        When a clone has occurred on a run on another :code:`bobocep` instance.

        :param nfa_name: The NFA name.
        :type nfa_name: str

        :param run_id: The ID of the cloned run.
        :type run_id: str

        :param next_state_name: The state of the cloned run.
        :type next_state_name: str

        :param next_event: The event of the cloned run.
        :type next_event: BoboEvent
        """

    @abstractmethod
    def on_dist_run_halt(self,
                         nfa_name: str,
                         run_id: str) -> None:
        """
        When a run has halted on a run on another :code:`bobocep` instance.

        :param nfa_name: The NFA name.
        :type nfa_name: str

        :param run_id: The ID of the halted run.
        :type run_id: str
        """

    @abstractmethod
    def on_sync_response(self,
                         sync_id: str,
                         body: str) -> None:
        """
        The response from another :code:`bobocep` instance when attempting to
        synchronise decider state across instances.

        :param sync_id: The ID of the synchronise request.
        :type sync_id: str

        :param body: The body of the response containing synchronise data.
        :type body: str
        """
