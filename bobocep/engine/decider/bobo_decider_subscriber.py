from abc import abstractmethod

from bobocep.events.bobo_event_composite import BoboEventComposite


class BoboDeciderSubscriber:

    def __init__(self):
        super().__init__()

    @abstractmethod
    def on_decider_composite_event(self, event: BoboEventComposite):
        """"""
