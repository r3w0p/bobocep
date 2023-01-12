# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC, abstractmethod

from bobocep.cep.event import BoboEventAction


class BoboForwarderSubscriber(ABC):
    """A forwarder subscriber interface."""

    @abstractmethod
    def on_forwarder_update(self, event: BoboEventAction):
        """"""


class BoboForwarderPublisher(ABC):
    """A forwarder publisher interface."""

    def __init__(self):
        super().__init__()

        self._subscribers = []

    def subscribe(self, subscriber: BoboForwarderSubscriber):
        """
        :param subscriber: Subscriber to add to list.
        """
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)
