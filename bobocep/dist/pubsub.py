# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC, abstractmethod
from typing import List

from bobocep.cep.engine.decider.runtup import BoboRunTuple

"""
Distributed publish-subscriber classes.
"""


class BoboDistributedSubscriber(ABC):
    """A distributed subscriber interface."""

    @abstractmethod
    def on_distributed_update(
            self,
            completed: List[BoboRunTuple],
            halted: List[BoboRunTuple],
            updated: List[BoboRunTuple]):
        """"""


class BoboDistributedPublisher(ABC):
    """A distributed publisher interface."""

    @abstractmethod
    def subscribe(self, subscriber: BoboDistributedSubscriber):
        """"""
