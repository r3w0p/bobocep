# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional


class BoboJSONable(ABC):

    @abstractmethod
    def to_json_str(self) -> str:
        """"""

    @staticmethod
    @abstractmethod
    def from_json_str(j: str) -> 'BoboJSONable':
        """"""
