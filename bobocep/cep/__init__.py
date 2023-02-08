# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Complex event processing functionality.
"""

from abc import ABC, abstractmethod

from bobocep import BoboError


class BoboJSONableError(BoboError):
    """A JSONable error."""


class BoboJSONable(ABC):
    """A abstract interface for JSONable types."""

    @abstractmethod
    def to_json_str(self) -> str:
        """
        :return: A JSON `str` representation of object of this type.
        """

    @staticmethod
    @abstractmethod
    def from_json_str(j: str) -> 'BoboJSONable':
        """
        :param j: A JSON `str` representation of object of this type.
        :return: A new instance of this type.
        """

    @staticmethod
    @abstractmethod
    def from_dict(d: dict) -> 'BoboJSONable':
        """
        :param d: A `dict` representation of an object of this type.
        :return: A new instance of this type.
        """
