# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC, abstractmethod
from typing import List

from bobocep.cep.engine.task.decider import BoboRunTuple


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

    def __init__(self):
        super().__init__()

        self._subscribers = []

    def subscribe(self, subscriber: BoboDistributedSubscriber):
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)
