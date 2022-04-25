# Copyright (c) 2022 The BoboCEP Authors
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from bobocep.engine.decider.bobo_decider_subscriber import \
    BoboDeciderSubscriber


class BoboDeciderPublisher:

    def __init__(self):
        super().__init__()

        self._subscribers = []

    def subscribe(self, subscriber: BoboDeciderSubscriber):
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)
