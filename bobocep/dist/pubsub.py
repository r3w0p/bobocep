# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Distributed publish-subscribe classes.
"""

from abc import ABC, abstractmethod
from typing import List

from bobocep.cep.engine.decider.runserial import BoboRunSerial


class BoboDistributedSubscriber(ABC):
    """A distributed subscriber interface."""

    @abstractmethod
    def on_distributed_update(
            self,
            completed: List[BoboRunSerial],
            halted: List[BoboRunSerial],
            updated: List[BoboRunSerial]) -> None:
        """
        :param completed: Completed runs.
        :param halted: Halted runs.
        :param updated: Updated runs.
        """


class BoboDistributedPublisher(ABC):
    """A distributed publisher interface."""

    @abstractmethod
    def subscribe(self, subscriber: BoboDistributedSubscriber) -> None:
        """
        :param subscriber: Subscriber to distributed.
        """
