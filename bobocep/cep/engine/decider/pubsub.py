# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Decider publish-subscribe classes.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple

from bobocep.cep.engine.decider.runserial import BoboRunSerial


class BoboDeciderSubscriber(ABC):
    """
    A decider subscriber interface.
    """

    @abstractmethod
    def on_decider_update(
            self,
            completed: List[BoboRunSerial],
            halted: List[BoboRunSerial],
            updated: List[BoboRunSerial],
            local: bool
    ) -> None:
        """
        :param completed: Completed runs.
        :param halted: Halted runs.
        :param updated: Updated runs.
        :param local: `True` if the Decider update occurred locally;
            `False` if the update occurred on a remote (distributed) instance.
        """


class BoboDeciderPublisher(ABC):
    """
    A decider publisher interface.
    """

    @abstractmethod
    def subscribe(self, subscriber: BoboDeciderSubscriber):
        """
        :param subscriber: Subscriber to add to list.
        """

    @abstractmethod
    def snapshot(self) -> Tuple[
        List[BoboRunSerial], List[BoboRunSerial], List[BoboRunSerial]
    ]:
        """
        A snapshot of the current state of the Decider.

        :return: Tuple of cached completed, cached halted, and
            currently partially-completed runs.
            If caching is disabled, the first two lists will be empty.
        """
