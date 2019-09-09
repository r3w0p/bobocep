from abc import ABC, abstractmethod

from bobocep.rules.events.primitive_event import PrimitiveEvent


class IReceiverSubscriber(ABC):
    """An interface to subscribe to Receiver events."""

    @abstractmethod
    def on_receiver_event(self, event: PrimitiveEvent):
        """
        When a Receiver has generated a new PrimitiveEvent instance.

        :param event: A new event.
        :type event: BoboEvent
        """

    @abstractmethod
    def on_invalid_data(self, data):
        """
        When a Receiver rejects data because it does not pass validity checks.

        :param data: Invalid data.
        :type data: any
        """
