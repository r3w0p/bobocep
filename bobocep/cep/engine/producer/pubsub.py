# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from abc import ABC, abstractmethod

from bobocep.cep.event import BoboEventComplex


class BoboProducerSubscriber(ABC):
    """A producer subscriber interface."""

    @abstractmethod
    def on_producer_update(self, event: BoboEventComplex):
        """"""


class BoboProducerPublisher(ABC):
    """A producer publisher interface."""

    @abstractmethod
    def subscribe(self, subscriber: BoboProducerSubscriber):
        """
        :param subscriber: Subscriber to add to list.
        """