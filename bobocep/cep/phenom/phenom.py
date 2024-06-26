# Copyright (c) 2019-2024 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
A phenomenon.
"""

from inspect import signature
from types import MethodType
from typing import Callable, List, Tuple, Optional

from bobocep import BoboError
from bobocep.cep.action.action import BoboAction
from bobocep.cep.phenom.pattern.pattern import BoboPattern

_EXC_NAME_LEN = "name must have a length greater than 0"
_EXC_INVALID_CALL = "datagen callable must have {} parameters, found {}"
_LEN_PARAM_DATAGEN = 2


class BoboPhenomenonError(BoboError):
    """
    A phenomenon error.
    """


class BoboPhenomenon:
    """
    A phenomenon, satisfied by patterns of events, which facilitates the
    generating of complex events
    """

    def __init__(self,
                 name: str,
                 patterns: List[BoboPattern],
                 action: Optional[BoboAction] = None,
                 datagen: Optional[Callable] = None,
                 retain: bool = True):
        """
        :param name: Phenomenon name.
        :param patterns: Phenomenon patterns.
        :param action: Phenomenon action.
        :param datagen: Phenomenon datagen.
        :param retain: If `True`, retains datagen callable as an object
            variable to prevent garbage collection of it.
        """
        super().__init__()

        if len(name) == 0:
            raise BoboPhenomenonError(_EXC_NAME_LEN)

        if datagen is not None:
            len_param_datagen = len(signature(datagen).parameters)

            if len_param_datagen != _LEN_PARAM_DATAGEN:
                raise BoboPhenomenonError(
                    _EXC_INVALID_CALL.format(
                        _LEN_PARAM_DATAGEN,
                        len_param_datagen))

            # Prevent garbage collection of object if callable is a method.
            self._obj = datagen.__self__ \
                if retain and isinstance(datagen, MethodType) else None

        self._name: str = name
        self._patterns: Tuple[BoboPattern, ...] = tuple(patterns)
        self._datagen: Optional[Callable] = datagen
        self._action: Optional[BoboAction] = action
        self._retain: bool = retain

    @property
    def name(self) -> str:
        """
        :return: Phenomenon name.
        """
        return self._name

    @property
    def patterns(self) -> Tuple[BoboPattern, ...]:
        """
        :return: Phenomenon patterns.
        """
        return self._patterns

    @property
    def datagen(self) -> Optional[Callable]:
        """
        :return: Phenomenon datagen, or `None`.
        """
        return self._datagen

    @property
    def action(self) -> Optional[BoboAction]:
        """
        :return: Phenomenon action, or `None`.
        """
        return self._action

    @property
    def retain(self) -> bool:
        """
        :return: True if retains datagen callable; False otherwise.
        """
        return self._retain
