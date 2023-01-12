# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC, abstractmethod
from typing import List

from bobocep.cep.engine.task.decider.run import BoboDeciderRunTuple


class BoboDeciderSubscriber(ABC):
    """A decider subscriber interface."""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def on_decider_update(
            self,
            halted_complete: List[BoboDeciderRunTuple],
            halted_incomplete: List[BoboDeciderRunTuple],
            updated: List[BoboDeciderRunTuple]):
        """"""


class BoboDeciderPublisher(ABC):
    """A decider publisher interface."""

    def __init__(self):
        super().__init__()

        self._subscribers = []

    def subscribe(self, subscriber: BoboDeciderSubscriber):
        """
        :param subscriber: Subscriber to add to list.
        """
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)
