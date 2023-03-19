# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from abc import ABC, abstractmethod
from typing import List
from bobocep.cep.engine.decider import BoboRunTuple

"""
Decider publish-subscriber classes.
"""


class BoboDeciderSubscriber(ABC):
    """
    A decider subscriber interface.
    """

    @abstractmethod
    def on_decider_update(
            self,
            completed: List[BoboRunTuple],
            halted: List[BoboRunTuple],
            updated: List[BoboRunTuple]):
        """"""


class BoboDeciderPublisher(ABC):
    """
    A decider publisher interface.
    """

    @abstractmethod
    def subscribe(self, subscriber: BoboDeciderSubscriber):
        """
        :param subscriber: Subscriber to add to list.
        """
