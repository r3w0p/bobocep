# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC

from bobocep.engine.receiver.bobo_receiver_subscriber import \
    BoboReceiverSubscriber


class BoboReceiverPublisher(ABC):

    def __init__(self):
        super().__init__()

        self._subscribers = []

    def subscribe(self, subscriber: BoboReceiverSubscriber):
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)
