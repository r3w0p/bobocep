# Copyright (c) The BoboCEP Authors
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from typing import Callable, List

from bobocep.events.bobo_event import BoboEvent
from bobocep.events.bobo_history import BoboHistory
from bobocep.predicate.bobo_predicate_callable import BoboPredicateCallable


class BoboPredicateCallableType(BoboPredicateCallable):
    """A predicate that evaluates using a custom function or method after
       first checking whether the event data type matches given types.

    :param types: A list of valid data types. The event's data type must match
                  at least one.
    :type types: List[type]

    :param subtype: If True, it will match subtypes of types, equivalent to
                    isinstance() functionality.
                    If False, it will match exact types only, equivalent to
                    type() functionality.
    :type subtype: bool
    """

    def __init__(self,
                 call: Callable,
                 types: List[type],
                 subtype: bool = True):
        super().__init__(call=call)

        self._types = types
        self._subtype = subtype

    def evaluate(self, event: BoboEvent, history: BoboHistory) -> bool:
        if self._subtype:
            if not any(isinstance(event.data, t) for t in self._types):
                return False
        else:
            if not any(type(event.data) == t for t in self._types):
                return False

        return self._call(event, history)