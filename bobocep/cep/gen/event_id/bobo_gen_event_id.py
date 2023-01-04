# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from abc import ABC, abstractmethod


class BoboGenEventID(ABC):
    """An event ID generator."""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def generate(self) -> str:
        """"""
