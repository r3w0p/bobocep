# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from abc import ABC, abstractmethod

from dpcontracts import require, ensure

from bobocep.event.bobo_event import BoboEvent
from bobocep.event.bobo_history import BoboHistory


class BoboPredicate(ABC):
    """A predicate that evaluates to either True or False."""

    @abstractmethod
    @require("'event' must be an instance of BoboEvent",
             lambda args: isinstance(args.event, BoboEvent))
    @require("'history' must be an instance of BoboHistory",
             lambda args: isinstance(args.history, BoboHistory))
    @ensure("result must be an instance of bool",
            lambda args, result: isinstance(result, bool))
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
