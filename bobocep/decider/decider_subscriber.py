from abc import ABC, abstractmethod

from bobocep.rules.events.composite_event import CompositeEvent


class IDeciderSubscriber(ABC):
    """An interface to subscribe to Decider events."""

    @abstractmethod
    def on_decider_complex_event(self, event: CompositeEvent):
        """
        When a Decider identifies a complex event in the event stream.

        :param event: The complex event.
        :type event: CompositeEvent
        """
