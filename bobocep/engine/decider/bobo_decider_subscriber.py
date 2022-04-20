# Copyright (c) The BoboCEP Authors
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License v3.0.

from abc import abstractmethod

from bobocep.engine.decider.bobo_decider_run import BoboDeciderRun


class BoboDeciderSubscriber:

    def __init__(self):
        super().__init__()

    @abstractmethod
    def on_decider_completed_run(self, run: BoboDeciderRun):
        """"""
