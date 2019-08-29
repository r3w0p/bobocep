from abc import ABC, abstractmethod

from bobocep.rules.events.composite_event import CompositeEvent


class IForwarderSubscriber(ABC):
    """An interface to subscribe to Forwarder events."""

    @abstractmethod
    def on_forwarder_success_event(self, event: CompositeEvent) -> None:
        """
        Events that have been successfully forwarded.

        :param event: A successful event.
        :type event: CompositeEvent
        """

    @abstractmethod
    def on_forwarder_failure_event(self, event: CompositeEvent) -> None:
        """
        Events that failed to be forwarded.

        :param event: An unsuccessful event.
        :type event: CompositeEvent
        """
