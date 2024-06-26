# Copyright (c) 2019-2024 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Tools to help with `BoboCEP` setup.
"""

from abc import ABC, abstractmethod
from typing import Any

from bobocep import BoboError


class BoboSetupError(BoboError):
    """
    A setup error.
    """


class BoboSetup(ABC):
    """
    A setup.
    """

    @abstractmethod
    def generate(self) -> Any:
        """
        :return: Relevant setup data.
        """
