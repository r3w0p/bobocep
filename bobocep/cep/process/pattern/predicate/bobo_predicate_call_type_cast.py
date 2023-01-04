# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from typing import Callable

from bobocep.cep.event.bobo_event import BoboEvent
from bobocep.cep.event.bobo_history import BoboHistory
from bobocep.cep.process.pattern.predicate.bobo_predicate_call import \
    BoboPredicateCall


class BoboPredicateCallTypeCast(BoboPredicateCall):
    """A predicate that evaluates using a custom function or method after
       first checking whether the event's data can be cast to a given type."""

    def __init__(self,
                 call: Callable,
                 dtype: type):
        super().__init__(call=call)

        self._dtype: type = dtype

    def evaluate(self, event: BoboEvent, history: BoboHistory) -> bool:
        try:
            self._dtype(event.data)

        except ValueError:
            return False

        return self._call(event, history)
