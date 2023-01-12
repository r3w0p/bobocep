# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC, abstractmethod

from bobocep.cep.event import BoboEvent


class BoboReceiverSubscriber(ABC):
    """A receiver subscriber interface."""

    @abstractmethod
    def on_receiver_update(self, event: BoboEvent) -> None:
        """
        :param event: New BoboEvent instance processed by the receiver.
        """


class BoboReceiverPublisher(ABC):
    """A receiver publisher interface."""

    def __init__(self):
        super().__init__()

        self._subscribers = []

    def subscribe(self, subscriber: BoboReceiverSubscriber) -> None:
        """
        :param subscriber: Subscriber to add to list.
        """
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)
