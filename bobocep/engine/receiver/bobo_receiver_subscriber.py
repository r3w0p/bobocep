# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from abc import abstractmethod

from bobocep.event.bobo_event import BoboEvent


class BoboReceiverSubscriber:

    def __init__(self):
        super().__init__()

    @abstractmethod
    def on_receiver_event(self, event: BoboEvent):
        """"""
