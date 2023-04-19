# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from typing import Tuple, Any

from bobocep.cep.action.action import BoboAction
from bobocep.cep.event import BoboEventComplex


class BoboActionTrue(BoboAction):
    """An action that is always successful."""

    def __init__(self, name: str = "action"):
        super().__init__(name)

    def execute(self, event: BoboEventComplex) -> Tuple[bool, Any]:
        return True, True


class BoboActionFalse(BoboAction):
    """
    An action that is always unsuccessful
    """

    def __init__(self, name: str = "action"):
        super().__init__(name)

    def execute(self, event: BoboEventComplex) -> Tuple[bool, Any]:
        return False, False


class BoboActionRuntimeError(BoboAction):
    """An action that always throws a RuntimeError."""

    def __init__(self, name: str = "action"):
        super().__init__(name)

    def execute(self, event: BoboEventComplex) -> Tuple[bool, Any]:
        raise RuntimeError()
