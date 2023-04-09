# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Receiver publish-subscribe classes.
"""

from abc import ABC, abstractmethod

from bobocep.cep.event import BoboEvent


class BoboReceiverSubscriber(ABC):
    """
    A receiver subscriber interface.
    """

    @abstractmethod
    def on_receiver_update(self, event: BoboEvent) -> None:
        """
        :param event: A new BoboEvent instance processed by the receiver.
        """


class BoboReceiverPublisher(ABC):
    """
    A receiver publisher interface.
    """

    @abstractmethod
    def subscribe(self, subscriber: BoboReceiverSubscriber) -> None:
        """
        :param subscriber: Subscriber to add to list.
        """
