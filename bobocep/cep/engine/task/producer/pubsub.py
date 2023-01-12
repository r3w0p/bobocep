# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC, abstractmethod

from bobocep.cep.event import BoboEventComplex


class BoboProducerSubscriber(ABC):
    """A producer subscriber interface."""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def on_producer_update(self, event: BoboEventComplex):
        """"""


class BoboProducerPublisher(ABC):
    """A producer publisher interface."""

    def __init__(self):
        super().__init__()

        self._subscribers = []

    def subscribe(self, subscriber: BoboProducerSubscriber):
        """
        :param subscriber: Subscriber to add to list.
        """
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)
