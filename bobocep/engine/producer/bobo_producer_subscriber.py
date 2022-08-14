# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC, abstractmethod

from bobocep.event.bobo_event_complex import BoboEventComplex


class BoboProducerSubscriber(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def on_producer_complex_event(self, event: BoboEventComplex):
        """"""
