# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from inspect import signature
from types import MethodType
from typing import Callable, List, Tuple, Union

from bobocep.action.bobo_action import BoboAction
from bobocep.exception.bobo_predicate_invalid_callable_error import \
    BoboPredicateInvalidCallableError
from bobocep.pattern.bobo_pattern import BoboPattern


class BoboProcess:
    """A process."""

    _EXC_INVALID_CALL = "'datagen' must have {0} parameters, found {1}"
    _LEN_PARAM_DATAGEN = 2

    def __init__(self,
                 name: str,
                 patterns: List[BoboPattern],
                 datagen: Callable,
                 action: Union[BoboAction, None]):
        super().__init__()

        if len(name) == 0:
            pass  # todo raise exception

        len_param_datagen = len(signature(datagen).parameters)

        if len_param_datagen != self._LEN_PARAM_DATAGEN:
            raise BoboPredicateInvalidCallableError(
                self._EXC_INVALID_CALL.format(self._LEN_PARAM_DATAGEN,
                                              len_param_datagen))

        self.name: str = name
        self.patterns: Tuple[BoboPattern, ...] = tuple(patterns)
        self.datagen: Callable = datagen
        self.action: BoboAction = action

        # Prevent garbage collection of object if callable is a method.
        self._obj = datagen.__self__ \
            if isinstance(datagen, MethodType) else None
