from abc import ABC, abstractmethod

from bobocep.rules.events.bobo_event import BoboEvent


class IForwarderSubscriber(ABC):
    """An interface to subscribe to Forwarder events."""

    @abstractmethod
    def on_forwarder_success_event(self, event: BoboEvent):
        """
        Events that have been successfully forwarded.

        :param event: A successful event.
        :type event: BoboEvent
        """

    @abstractmethod
    def on_forwarder_failure_event(self, event: BoboEvent):
        """
        Events that failed to be forwarded.

        :param event: An unsuccessful event.
        :type event: BoboEvent
        """
