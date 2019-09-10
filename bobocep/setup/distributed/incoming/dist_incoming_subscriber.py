from abc import ABC, abstractmethod

from bobocep.rules.events.action_event import ActionEvent
from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory


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
    def on_dist_run_final(self,
                          nfa_name: str,
                          run_id: str,
                          history: BoboHistory) -> None:
        """
        When a run has reached its final state on another :code:`bobocep`
        instance.

        :param nfa_name: The NFA name.
        :type nfa_name: str

        :param run_id: The ID of the accepted run.
        :type run_id: str

        :param history: The history of the accepted run.
        :type history: BoboHistory
        """

    @abstractmethod
    def on_dist_action(self, event: ActionEvent) -> None:
        """
        When an action is executed on another :code:`bobocep`
        instance.

        :param event: The action event.
        :type event: ActionEvent
        """
