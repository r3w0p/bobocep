# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from abc import ABC, abstractmethod
from typing import Optional

from bobocep.cep.event.bobo_event import BoboEvent


class BoboEventGen(ABC):
    """An event generator."""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def maybe_generate(self, event_id: str) -> Optional[BoboEvent]:
        """"""
