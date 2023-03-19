# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Action definitions.
"""

from abc import ABC, abstractmethod

from bobocep import BoboError


_EXC_NAME_LEN = "name must have a length greater than 0"


class BoboActionError(BoboError):
    """
    An action error.
    """


class BoboAction(ABC):
    from bobocep.cep.event import BoboEventComplex, BoboEventAction
    """
    An action.
    """

    def __init__(self, name: str, *args, **kwargs):
        """
        :param name: The action name.
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
        Get action name.
        """
        return self._name

    @abstractmethod
    def execute(self, event: BoboEventComplex) -> BoboEventAction:
        """
        :param event: The complex event that triggered action.
        :return: An action event describing the action and its effect.
        """
