# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from typing import Callable

from src.cep.event.bobo_event import BoboEvent
from src.cep.event.bobo_history import BoboHistory
from src.cep.process.pattern.predicate.bobo_predicate_call import \
    BoboPredicateCall


class BoboPredicateCallInstanceOf(BoboPredicateCall):
    """A predicate that evaluates using a custom function or method after
       first checking whether the event data is an instance of a given type."""

    def __init__(self,
                 call: Callable,
                 dtype: type,
                 subtype: bool = True):
        super().__init__(call=call)

        self._dtype: type = dtype
        self._subtype: bool = subtype

    def evaluate(self, event: BoboEvent, history: BoboHistory) -> bool:
        if self._subtype:
            if not isinstance(event.data, self._dtype):
                return False
        else:
            if not type(event.data) == self._dtype:
                return False

        return self._call(event, history)
