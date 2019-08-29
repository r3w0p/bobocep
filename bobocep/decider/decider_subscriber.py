from abc import ABC, abstractmethod

from bobocep.rules.events.histories.bobo_history import BoboHistory


class IDeciderSubscriber(ABC):
    """An interface to subscribe to Decider events."""

    @abstractmethod
    def on_decider_complex_event(self,
                                 nfa_name: str,
                                 history: BoboHistory) -> None:
        """
        When a Decider identifies a complex event in the event stream.

        :param nfa_name: The complex event name.
        :type nfa_name: str

        :param history: The events that triggered the complex event.
        :type history: BoboHistory
        """
