# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from abc import ABC, abstractmethod
from typing import Any


class BoboValidator(ABC):
    """A validator for data of any type."""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def is_valid(self, data: Any) -> bool:
        """"""
