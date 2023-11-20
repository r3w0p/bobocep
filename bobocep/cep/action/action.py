# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Action definitions.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Any

from bobocep import BoboError
from bobocep.cep.event import BoboEventComplex

_EXC_NAME_LEN = "name must have a length greater than 0"


class BoboActionError(BoboError):
    """
    An action error.
    """


class BoboAction(ABC):
    """
    An action.
    """

    def __init__(self, name: str, *args, **kwargs):
        """
        :param name: The action name.
        :param args: Action arguments.
        :param kwargs: Action keyword arguments.
        """
        super().__init__()

        if len(name) == 0:
            raise BoboActionError(_EXC_NAME_LEN)

        self._name = name
        self._args = args
        self._kwargs = kwargs

    @property
    def name(self) -> str:
        """
        :return: Action name.
        """
        return self._name

    @abstractmethod
    def execute(self, event: BoboEventComplex) -> Tuple[bool, Any]:
        """
        :param event: The complex event that triggered the action.

        :return: A tuple containing:
                 whether the action execution was successful; and
                 any additional data.
        """
