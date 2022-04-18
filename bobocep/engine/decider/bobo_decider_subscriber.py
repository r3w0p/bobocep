# Copyright (c) 2022, The BoboCEP Contributors
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License v3.0.

from abc import abstractmethod

from bobocep.events.bobo_event_composite import BoboEventComposite


class BoboDeciderSubscriber:

    def __init__(self):
        super().__init__()

    @abstractmethod
    def on_decider_composite_event(self, event: BoboEventComposite):
        """"""
