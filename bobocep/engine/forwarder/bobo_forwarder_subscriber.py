# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC, abstractmethod

from bobocep.action.bobo_action_response import \
    BoboActionResponse


class BoboForwarderSubscriber(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def on_forwarder_action_response(self, response: BoboActionResponse):
        """"""
