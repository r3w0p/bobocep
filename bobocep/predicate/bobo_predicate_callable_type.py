from typing import Callable

from dpcontracts import require

from bobocep.events.bobo_event import BoboEvent
from bobocep.events.bobo_history import BoboHistory
from bobocep.predicate.bobo_predicate_callable import BoboPredicateCallable


class BoboPredicateCallableType(BoboPredicateCallable):
    """A predicate that evaluates using a custom function or method after
       first checking whether the event data type matches a given type.
       False is returned if the types do not match.

    :param data_type: The data type that the event's data type must match.
    :type data_type: type
    """

    @require("'data_type' must be an instance of type",
             lambda args: isinstance(args.data_type, type))
    def __init__(self, call: Callable, data_type: type):
        super().__init__(call=call)

        self.data_type = data_type

    def evaluate(self, event: BoboEvent, history: BoboHistory) -> bool:
        if not isinstance(event.data, self.data_type):
            return False

        return self._call(event, history)
