# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from typing import Callable, Tuple, List

from src.cep.event.bobo_event import BoboEvent
from src.cep.event.bobo_history import BoboHistory
from src.cep.process.pattern.predicate.bobo_predicate_call import \
    BoboPredicateCall


class BoboPredicateCallType(BoboPredicateCall):
    """A predicate that evaluates using a custom function or method after
       first checking whether the event data type matches given types."""

    def __init__(self,
                 call: Callable,
                 types: List[type],
                 subtype: bool = True):
        super().__init__(call=call)

        self._types: Tuple[type, ...] = tuple(types)
        self._subtype = subtype

    def evaluate(self, event: BoboEvent, history: BoboHistory) -> bool:
        if self._subtype:
            if not any(isinstance(event.data, t) for t in self._types):
                return False
        else:
            if not any(type(event.data) == t for t in self._types):
                return False

        return self._call(event, history)
