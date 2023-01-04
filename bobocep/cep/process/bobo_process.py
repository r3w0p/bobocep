# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from inspect import signature
from types import MethodType
from typing import Callable, List, Tuple, Optional

from bobocep.cep.action.bobo_action import BoboAction
from bobocep.cep.process.bobo_process_error import BoboProcessError
from bobocep.cep.process.pattern.bobo_pattern import BoboPattern


class BoboProcess:
    """A process."""

    _EXC_NAME_LEN = "name must have a length greater than 0"
    _EXC_INVALID_CALL = "datagen must have {} parameters if callable, found {}"
    _LEN_PARAM_DATAGEN = 2

    def __init__(self,
                 name: str,
                 patterns: List[BoboPattern],
                 action: Optional[BoboAction],
                 datagen: Optional[Callable] = None,
                 retain: bool = True):
        super().__init__()

        if len(name) == 0:
            raise BoboProcessError(self._EXC_NAME_LEN)

        if datagen is not None:
            len_param_datagen = len(signature(datagen).parameters)

            if len_param_datagen != self._LEN_PARAM_DATAGEN:
                raise BoboProcessError(
                    self._EXC_INVALID_CALL.format(
                        self._LEN_PARAM_DATAGEN,
                        len_param_datagen))

            # Prevent garbage collection of object if callable is a method.
            self._obj = datagen.__self__ \
                if retain and isinstance(datagen, MethodType) else None

        self.name: str = name
        self.patterns: Tuple[BoboPattern, ...] = tuple(patterns)
        self.datagen: Optional[Callable] = datagen
        self.action: Optional[BoboAction] = action


