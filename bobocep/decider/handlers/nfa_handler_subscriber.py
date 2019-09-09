from abc import ABC, abstractmethod

from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.composite_event import CompositeEvent


class INFAHandlerSubscriber(ABC):

    @abstractmethod
    def on_handler_transition(self,
                              nfa_name: str,
                              run_id: str,
                              state_name_from: str,
                              state_name_to: str,
                              event: BoboEvent):
        """
        Triggers a response when a state transition occurs in a run.

        :param nfa_name: The NFA name.
        :type nfa_name: str

        :param run_id: The run ID.
        :type run_id: str

        :param state_name_from: The original state before the transition.
        :type state_name_from: str

        :param state_name_to: The new state after the transition.
        :type state_name_to: str

        :param event: The event that caused the state transition.
        :type event: BoboEvent
        """

    @abstractmethod
    def on_handler_clone(self,
                         nfa_name: str,
                         run_id: str,
                         state_name: str,
                         event: BoboEvent):
        """Triggers a response when a clone occurs in a run. Newly created runs
        are considered to be cloned but without a parent run.

        :param nfa_name: The NFA name.
        :type nfa_name: str

        :param run_id: The cloned run ID.
        :type run_id: str

        :param state_name: The state of the cloned run.
        :type state_name: str

        :param event: The event that caused the clone.
        :type event: BoboEvent
        """

    @abstractmethod
    def on_handler_final(self,
                         nfa_name: str,
                         run_id: str,
                         event: CompositeEvent):
        """Triggers a response when a run reaches its final state.

        :param nfa_name: The NFA name.
        :type nfa_name: str

        :param run_id: The run ID.
        :type run_id: str

        :param event: The complex event.
        :type event: CompositeEvent
        """

    @abstractmethod
    def on_handler_halt(self,
                        nfa_name: str,
                        run_id: str):
        """Triggers a response when a run halts. This occurs if a run reaches
        its final state, or if a run halts prematurely.

        :param nfa_name: The NFA name.
        :type nfa_name: str

        :param run_id: The run ID.
        :type run_id: str
        """
