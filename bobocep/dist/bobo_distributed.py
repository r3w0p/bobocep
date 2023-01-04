# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from abc import ABC, abstractmethod

from bobocep.cep.engine.decider.bobo_decider_subscriber import \
    BoboDeciderSubscriber
from bobocep.cep.engine.forwarder.bobo_forwarder_subscriber import \
    BoboForwarderSubscriber
from bobocep.cep.engine.producer.bobo_producer_subscriber import \
    BoboProducerSubscriber
from bobocep.cep.engine.receiver.bobo_receiver_subscriber import \
    BoboReceiverSubscriber
from bobocep.dist.bobo_distributed_publisher import \
    BoboDistributedPublisher


class BoboDistributed(BoboDistributedPublisher,
                      BoboReceiverSubscriber,
                      BoboDeciderSubscriber,
                      BoboProducerSubscriber,
                      BoboForwarderSubscriber,
                      ABC):
    """A class for enabling BoboCEP to be distributed over the network."""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def run(self):
        """"""
