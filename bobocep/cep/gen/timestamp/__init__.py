# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""BoboEvent timestamp generators."""

from abc import ABC, abstractmethod
from time import time_ns


class BoboGenTimestamp(ABC):
    """A timestamp generator."""

    @abstractmethod
    def generate(self) -> int:
        """"""


class BoboGenTimestampEpoch(BoboGenTimestamp):
    """A timestamp generator that returns the current time in milliseconds
    since the Epoch."""

    def generate(self) -> int:
        return time_ns() // 1000000
