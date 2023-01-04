# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from abc import ABC, abstractmethod

from bobocep.cep.event.bobo_event import BoboEvent


class BoboReceiverSubscriber(ABC):
    """A receiver subscriber interface."""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def on_receiver_update(self, event: BoboEvent):
        """"""
