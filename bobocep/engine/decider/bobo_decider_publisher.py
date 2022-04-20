# Copyright (c) The BoboCEP Authors
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License v3.0.

from bobocep.engine.decider.bobo_decider_subscriber import \
    BoboDeciderSubscriber


class BoboDeciderPublisher:

    def __init__(self):
        super().__init__()

        self._subscribers = []

    def subscribe(self, subscriber: BoboDeciderSubscriber):
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)
