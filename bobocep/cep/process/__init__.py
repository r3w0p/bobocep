# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""The process which data must follow in order to determine the occurrence of
a complex event."""

from inspect import signature
from types import MethodType
from typing import Callable, List, Tuple, Optional

from bobocep import BoboError
from bobocep.cep.action import BoboAction
from bobocep.cep.process.pattern import BoboPattern


class BoboProcessError(BoboError):
    """A process error."""


class BoboProcess:
    """A process."""

    _EXC_NAME_LEN = "'name' must have a length greater than 0"
    _EXC_INVALID_CALL = "'datagen' callable must have {} parameters, found {}"
    _LEN_PARAM_DATAGEN = 2

    def __init__(self,
                 name: str,
                 patterns: List[BoboPattern],
                 action: Optional[BoboAction] = None,
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

        self._name: str = name
        self._patterns: Tuple[BoboPattern, ...] = tuple(patterns)
        self._datagen: Optional[Callable] = datagen
        self._action: Optional[BoboAction] = action

    @property
    def name(self) -> str:
        """Get process name."""
        return self._name

    @property
    def patterns(self) -> Tuple[BoboPattern, ...]:
        """Get process patterns."""
        return self._patterns

    @property
    def datagen(self) -> Optional[Callable]:
        """Get process datagen."""
        return self._datagen

    @property
    def action(self) -> Optional[BoboAction]:
        """Get process action."""
        return self._action
