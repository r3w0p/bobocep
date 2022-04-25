# Copyright (c) 2022 The BoboCEP Authors
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from bobocep.engine.decider.bobo_decider import BoboDecider
from bobocep.engine.producer.bobo_producer import BoboProducer
from bobocep.engine.receiver.bobo_receiver import BoboReceiver


class BoboEngine:

    def __init__(self,
                 receiver: BoboReceiver,
                 decider: BoboDecider,
                 producer: BoboProducer):
        super().__init__()

        self.receiver = receiver
        self.decider = decider
        self.producer = producer

    def update(self) -> None:
        self.receiver.update()
        self.decider.update()
        self.producer.update()
