from abc import ABC, abstractmethod

from bobocep.rules.events.action_event import ActionEvent
from bobocep.rules.events.composite_event import CompositeEvent


class IProducerSubscriber(ABC):
    """An interface to subscribe to Producer events."""

    @abstractmethod
    def on_accepted_producer_event(self, event: CompositeEvent):
        """
        Complex events accepted by a Producer.

        :param event: An accepted event.
        :type event: CompositeEvent
        """

    @abstractmethod
    def on_rejected_producer_event(self, event: CompositeEvent):
        """
        Complex events rejected by a Producer.

        :param event: A rejected event.
        :type event: CompositeEvent
        """

    @abstractmethod
    def on_producer_action(self, event: ActionEvent):
        """
        When an action has been attempted by a BoboAction instance subscribed
        to a Producer.

        :param event: The action event.
        :type event: ActionEvent
        """
