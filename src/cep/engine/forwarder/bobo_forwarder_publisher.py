# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC

from src.cep.engine.forwarder.bobo_forwarder_subscriber import \
    BoboForwarderSubscriber


class BoboForwarderPublisher(ABC):

    def __init__(self):
        super().__init__()

        self._subscribers = []

    def subscribe(self, subscriber: BoboForwarderSubscriber):
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)
