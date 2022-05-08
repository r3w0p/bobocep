# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from abc import ABC, abstractmethod


class BoboValidator(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def is_valid(self, entity) -> bool:
        """"""
