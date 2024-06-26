# Copyright (c) 2019-2024 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
CEP engine tasks.
"""

from abc import ABC, abstractmethod

from bobocep import BoboError


class BoboEngineTaskError(BoboError):
    """
    An engine task error.
    """


class BoboEngineTask(ABC):
    """
    An engine task.
    """

    @abstractmethod
    def update(self) -> bool:
        """
        :return: `True` if an update occurred in the task; `False` otherwise.
        """

    @abstractmethod
    def size(self) -> int:
        """
        :return: The number of events that the task is currently handling.
        """

    @abstractmethod
    def close(self) -> None:
        """
        Closes the engine task.
        """

    @abstractmethod
    def is_closed(self) -> bool:
        """
        :return: `True` if task is set to close; `False` otherwise.
        """
