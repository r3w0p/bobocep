# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC

from src.dist.bobo_distributed_subscriber import \
    BoboDistributedSubscriber


class BoboDistributedPublisher(ABC):
    """A distributed publisher interface."""

    def __init__(self):
        super().__init__()

        self._subscribers = []

    def subscribe(self, subscriber: BoboDistributedSubscriber):
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)