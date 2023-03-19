# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Tools to help with `BoboCEP` setup.
"""

from abc import ABC, abstractmethod

from bobocep.cep.engine import BoboEngine


class BoboSetup(ABC):
    """
    A setup.
    """

    @abstractmethod
    def generate(self) -> BoboEngine:
        """
        :return: A BoboEngine instance with the chosen setup.
        """
