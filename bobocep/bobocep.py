# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Core classes.
"""

from abc import ABC, abstractmethod


class BoboError(Exception):
    """
    A `BoboCEP` error.
    """


class BoboJSONableError(BoboError):
    """
    A JSONable error.
    """


class BoboJSONable(ABC):
    """
    An abstract interface for JSONable types.
    """

    @abstractmethod
    def to_json_str(self) -> str:
        """
        :return: A JSON `str` representation of an object of this type.
        """

    @abstractmethod
    def to_json_dict(self) -> dict:
        """
        :return: A JSON `dict` representation of an object of this type.
        """

    @staticmethod
    @abstractmethod
    def from_json_str(j: str) -> 'BoboJSONable':
        """
        :param j: A JSON `str` representation of an object of this type.
        :return: A new instance of this type.
        """

    @staticmethod
    @abstractmethod
    def from_json_dict(d: dict) -> 'BoboJSONable':
        """
        :param d: A JSON `dict` representation of an object of this type.
        :return: A new instance of this type.
        """
