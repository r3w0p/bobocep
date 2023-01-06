# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from abc import ABC, abstractmethod
from typing import List

from bobocep.cep.engine.decider.bobo_decider_run_state import BoboDeciderRunState
from bobocep.cep.event.bobo_event import BoboEvent
from bobocep.cep.event.bobo_event_action import BoboEventAction
from bobocep.cep.event.bobo_event_complex import BoboEventComplex


class BoboDistributedSubscriber(ABC):
    """A distributed subscriber interface."""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def on_distributed_receiver_update(self, event: BoboEvent):
        """"""

    @abstractmethod
    def on_distributed_decider_update(
            self,
            halted_complete: List[BoboDeciderRunState],
            halted_incomplete: List[BoboDeciderRunState],
            updated: List[BoboDeciderRunState]):
        """"""

    @abstractmethod
    def on_distributed_producer_update(self, event: BoboEventComplex):
        """"""

    @abstractmethod
    def on_distributed_forwarder_update(self, event: BoboEventAction):
        """"""
