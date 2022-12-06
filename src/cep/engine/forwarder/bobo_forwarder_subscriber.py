# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC, abstractmethod

from src.cep.event.bobo_event_action import BoboEventAction


class BoboForwarderSubscriber(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def on_forwarder_update(self, event: BoboEventAction):
        """"""
