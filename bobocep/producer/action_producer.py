from bobocep.producer.bobo_producer import BoboProducer
from bobocep.rules.actions.bobo_action import BoboAction
from bobocep.rules.events.composite_event import CompositeEvent


class ActionProducer(BoboProducer):
    """An event producer that performs an action with a new CompositeEvent
    instance before passing it to the subscribers of the producer.

    :param action: The action to perform.
    :type action: BoboAction

    :param max_queue_size: The maximum data queue size,
                           defaults to 0 (infinite).
    :type max_queue_size: int, optional
    """

    def __init__(self,
                 action: BoboAction,
                 max_queue_size: int = 0) -> None:
        super().__init__(max_queue_size=max_queue_size)

        self._action = action

    def _handle_composite_event(self, event: CompositeEvent) -> bool:
        return self._action.execute(event)[0]
