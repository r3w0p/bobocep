# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC

from src.cep.engine.decider.bobo_decider_subscriber import \
    BoboDeciderSubscriber


class BoboDeciderPublisher(ABC):
    """A decider publisher interface."""

    def __init__(self):
        super().__init__()

        self._subscribers = []

    def subscribe(self, subscriber: BoboDeciderSubscriber):
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)
