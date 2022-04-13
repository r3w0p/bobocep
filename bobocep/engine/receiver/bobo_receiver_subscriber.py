from abc import abstractmethod

from bobocep.events.bobo_event import BoboEvent


class BoboReceiverSubscriber:

    def __init__(self):
        super().__init__()

    @abstractmethod
    def on_receiver_event(self, event: BoboEvent):
        """"""
