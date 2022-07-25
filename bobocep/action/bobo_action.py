# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC, abstractmethod

from bobocep.action.bobo_action_error import BoboActionError
from bobocep.action.bobo_action_response import \
    BoboActionResponse
from bobocep.event.bobo_event_complex import BoboEventComplex


class BoboAction(ABC):
    """An action."""

    _EXC_NAME_LEN = "'name' must have a length greater than 0"

    def __init__(self, name: str):
        super().__init__()

        if len(name) == 0:
            raise BoboActionError(self._EXC_NAME_LEN)

        self.name = name

    @abstractmethod
    def execute(self, event: BoboEventComplex) -> BoboActionResponse:
        """"""
