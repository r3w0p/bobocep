# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from typing import Callable

from bobocep.cep.event.bobo_event import BoboEvent
from bobocep.cep.event.bobo_history import BoboHistory
from bobocep.cep.process.pattern.predicate.bobo_predicate_call import \
    BoboPredicateCall


class BoboPredicateCallType(BoboPredicateCall):
    """A predicate that evaluates using a custom function or method after
       first checking whether the event data is an instance of a given type.
       If it is not, then a cast to the type can be attempted and a copy of
       the event is passed with its data cast to the type. Note that the
       copy is only used within the predicate, and the original event remains
       in use elsewhere."""

    def __init__(self,
                 call: Callable,
                 dtype: type,
                 subtype: bool = True,
                 cast: bool = True):
        super().__init__(call=call)

        self._dtype: type = dtype
        self._subtype: bool = subtype
        self._cast: bool = cast

    def evaluate(self, event: BoboEvent, history: BoboHistory) -> bool:
        ok_type: bool = True

        if self._subtype:
            # Checking type and subtypes
            if not isinstance(event.data, self._dtype):
                ok_type = False
        else:
            # Checking exact type only
            if not type(event.data) == self._dtype:
                ok_type = False

        if not ok_type:
            if self._cast:
                # Type does not match, attempting cast
                try:
                    event = event.cast(self._dtype)

                except (TypeError, ValueError):
                    # Cast failed
                    return False
            else:
                # Not attempting cast
                return False

        # Type match or successful cast
        return self._call(event, history)
