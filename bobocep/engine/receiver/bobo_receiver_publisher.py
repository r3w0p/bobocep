# Copyright (c) 2022, The BoboCEP Contributors
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License v3.0.

from bobocep.engine.receiver.bobo_receiver_subscriber import \
    BoboReceiverSubscriber


class BoboReceiverPublisher:

    def __init__(self):
        super().__init__()

        self._subscribers = []

    def subscribe(self, subscriber: BoboReceiverSubscriber):
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)
