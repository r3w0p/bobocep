# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC, abstractmethod

from bobocep.cep.action.bobo_action_error import BoboActionError
from bobocep.cep.event.bobo_event_action import BoboEventAction
from bobocep.cep.event.bobo_event_complex import BoboEventComplex


class BoboAction(ABC):
    """An action."""

    _EXC_NAME_LEN = "name must have a length greater than 0"

    def __init__(self, name: str, *args, **kwargs):
        super().__init__()

        if len(name) == 0:
            raise BoboActionError(self._EXC_NAME_LEN)

        self._name = name
        self._args = args
        self._kwargs = kwargs

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def execute(self, event: BoboEventComplex) -> BoboEventAction:
        """"""
