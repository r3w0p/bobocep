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
