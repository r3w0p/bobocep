# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC, abstractmethod
from typing import List

from bobocep.cep.engine.task.decider import BoboDeciderRunTuple
from bobocep.cep.event import BoboEvent, BoboEventComplex, BoboEventAction


class BoboDistributedSubscriber(ABC):
    """A distributed subscriber interface."""

    @abstractmethod
    def on_distributed_receiver_update(self, event: BoboEvent):
        """"""

    @abstractmethod
    def on_distributed_decider_update(
            self,
            halted_complete: List[BoboDeciderRunTuple],
            halted_incomplete: List[BoboDeciderRunTuple],
            updated: List[BoboDeciderRunTuple]):
        """"""

    @abstractmethod
    def on_distributed_producer_update(self, event: BoboEventComplex):
        """"""

    @abstractmethod
    def on_distributed_forwarder_update(self, event: BoboEventAction):
        """"""


class BoboDistributedPublisher(ABC):
    """A distributed publisher interface."""

    def __init__(self):
        super().__init__()

        self._subscribers = []

    def subscribe(self, subscriber: BoboDistributedSubscriber):
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)
