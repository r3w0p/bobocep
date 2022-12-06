# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from abc import ABC, abstractmethod
from typing import List

from src.cep.engine.decider.bobo_decider_run_tuple import BoboDeciderRunTuple
from src.cep.event.bobo_event import BoboEvent
from src.cep.event.bobo_event_action import BoboEventAction
from src.cep.event.bobo_event_complex import BoboEventComplex


class BoboDistributedSubscriber(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def on_distributed_receiver_update(self, event: BoboEvent):
        """"""

    @abstractmethod
    def on_distributed_decider_update(
            self,
            halted_complete: List[BoboDeciderRunTuple],
            halted_incomplete: List[BoboDeciderRunTuple],
            updated: List[BoboDeciderRunTuple]):
        """"""

    @abstractmethod
    def on_distributed_producer_update(self, event: BoboEventComplex):
        """"""

    @abstractmethod
    def on_distributed_forwarder_update(self, event: BoboEventAction):
        """"""
