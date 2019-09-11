from abc import ABC, abstractmethod

from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory


class IRunSubscriber(ABC):

    @abstractmethod
    def on_run_transition(self,
                          run_id: str,
                          state_name_from: str,
                          state_name_to: str,
                          event: BoboEvent,
                          notify: bool):
        """Triggers a response when a state transition occurs in a run.

        :param run_id: The run ID.
        :type run_id: str

        :param state_name_from: The original state before the transition.
        :type state_name_from: str

        :param state_name_to: The new state after the transition.
        :type state_name_to: str

        :param event: The event that caused the state transition.
        :type event: BoboEvent

        :param notify: Whether to notify handler subscribers of the transition.
        :type notify: bool
        """

    @abstractmethod
    def on_run_clone(self,
                     state_name: str,
                     event: BoboEvent,
                     parent_run_id: str,
                     force_parent: bool,
                     notify: bool):
        """Triggers a response when a clone occurs in a run. Newly created runs
        are considered to be cloned but without a parent run.

        :param state_name: The state of the cloned run.
        :type state_name: str

        :param event: The event that caused the clone.
        :type event: BoboEvent

        :param parent_run_id: The parent run ID, defaults to None.
        :type parent_run_id: str, optional

        :param force_parent: Ensures that a run is found with the parent run
                             ID. Otherwise, an exception is raised.
        :type force_parent: bool

        :param notify: Whether to notify handler subscribers of the clone.
        :type notify: bool
        """

    @abstractmethod
    def on_run_final(self,
                     run_id: str,
                     history: BoboHistory,
                     notify: bool):
        """Triggers a response when a run reaches its final state.

        :param run_id: The run ID.
        :type run_id: str

        :param history: The history of events that led to run completion.
        :type history: BoboHistory

        :param notify: Whether to notify handler subscribers of the run
                       reaching its final state.
        :type notify: bool
        """

    @abstractmethod
    def on_run_halt(self,
                    run_id: str,
                    notify: bool):
        """Triggers a response when a run halts. This occurs if a run reaches
        its final state, or if a run halts prematurely.

        :param run_id: The run ID.
        :type run_id: str

        :param notify: Whether to notify handler subscribers of the halting.
        :type notify: bool
        """
