# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC, abstractmethod


class BoboJSONable(ABC):
    """A JSONable class."""

    @abstractmethod
    def to_json_str(self) -> str:
        """"""

    @staticmethod
    @abstractmethod
    def from_json_str(j: str) -> 'BoboJSONable':
        """"""

    @staticmethod
    @abstractmethod
    def from_dict(d: dict) -> 'BoboJSONable':
        """"""
