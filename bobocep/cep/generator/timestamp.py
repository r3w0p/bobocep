# Copyright (c) 2019-2024 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Generates BoboEvent timestamps.
"""

from abc import ABC, abstractmethod
from time import time_ns


class BoboGenTimestamp(ABC):
    """
    A timestamp generator.
    """

    @abstractmethod
    def generate(self) -> int:
        """
        :return: Generated timestamp.
        """


class BoboGenTimestampEpoch(BoboGenTimestamp):
    """
    A timestamp generator that returns the current time, in milliseconds, since
    the Epoch.
    """

    def generate(self) -> int:
        """
        :return: The current time, in milliseconds, since the Epoch.
        """
        return time_ns() // 1000000
