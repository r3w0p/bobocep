# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from inspect import signature
from types import MethodType
from typing import Callable, List, Tuple, Union

from bobocep.action.bobo_action import BoboAction
from bobocep.process.pattern.bobo_pattern import BoboPattern
from bobocep.process.bobo_process_error import BoboProcessError


class BoboProcess:
    """A process."""

    _EXC_NAME_LEN = "'name' must have a length greater than 0"
    _EXC_INVALID_CALL = "'datagen' must have 2 parameters, found {1}"
    _LEN_PARAM_DATAGEN = 2

    def __init__(self,
                 name: str,
                 patterns: List[BoboPattern],
                 datagen: Callable,
                 action: Union[BoboAction, None],
                 retain: bool = True):
        super().__init__()

        if len(name) == 0:
            raise BoboProcessError(self._EXC_NAME_LEN)

        len_param_datagen = len(signature(datagen).parameters)

        if len_param_datagen != self._LEN_PARAM_DATAGEN:
            raise BoboProcessError(
                self._EXC_INVALID_CALL.format(
                    self._LEN_PARAM_DATAGEN,
                    len_param_datagen))

        self.name: str = name
        self.patterns: Tuple[BoboPattern, ...] = tuple(patterns)
        self.datagen: Callable = datagen
        self.action: BoboAction = action

        # Prevent garbage collection of object if callable is a method.
        self._obj = datagen.__self__ \
            if retain and isinstance(datagen, MethodType) else None
