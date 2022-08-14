# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from abc import ABC

from bobocep.event.bobo_event import BoboEvent
from bobocep.event.bobo_history import BoboHistory


class BoboPredicate(ABC):
    """A predicate that evaluates to either True or False."""

    def evaluate(self,
                 event: BoboEvent,
                 history: BoboHistory) -> bool:
        """Evaluates the predicate.

        :param event: An event.
        :type event: BoboEvent

        :param history: A history of events.
        :type history: BoboHistory

        :return: True if the predicate evaluates to True,
                 False otherwise.
        :rtype: bool
        """
