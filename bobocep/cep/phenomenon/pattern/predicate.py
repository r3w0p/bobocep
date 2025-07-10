# Copyright (c) 2019-2025 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
A predicate tested against an event that must evaluate to `True` for the
event to be accepted as being part of the manifestation of a complex event.
"""

from abc import ABC, abstractmethod
from inspect import signature
from types import MethodType
from typing import Callable

from bobocep import BoboError
from bobocep.cep.event import BoboEvent, BoboHistory

EXC_INVALID_PARAM = "call must have {} parameters, found {}"
LEN_PARAM_CALL = 2


class BoboPredicateError(BoboError):
    """
    A predicate error.
    """


class BoboPredicate(ABC):
    """
    A predicate that evaluates to either True or False.
    """

    @abstractmethod
    def evaluate(self,
                 event: BoboEvent,
                 history: BoboHistory) -> bool:
        """
        Evaluates the predicate.

        :param event: An event.
        :type event: BoboEvent

        :param history: A history of events.
        :type history: BoboHistory

        :return: True if the predicate evaluates to True,
                 False otherwise.
        :rtype: bool
        """


class BoboPredicateCall(BoboPredicate):
    """
    A predicate that evaluates using a custom function or method
    (i.e. a 'callable').
    """

    def __init__(self, call: Callable):
        """
        :param call: The callable to use for evaluating the predicate.
        """
        super().__init__()

        len_param_call = len(signature(call).parameters)

        if len_param_call != LEN_PARAM_CALL:
            raise BoboPredicateError(
                EXC_INVALID_PARAM.format(LEN_PARAM_CALL, len_param_call))

        self._call = call

        # Prevent garbage collection of object if callable is a method.
        self._obj = call.__self__ if isinstance(call, MethodType) else None

    def evaluate(self, event: BoboEvent, history: BoboHistory) -> bool:
        """
        :param event: The event used for evaluation.
        :param history: The history of currently accepted events.
        :return: `True` if predicate is satisfied; `False` otherwise.
        """
        return self._call(event, history)
