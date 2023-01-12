# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""A predicate tested against an event that must evaluate to `True` for the
event to be accepted as being part of the manifestation of a complex event."""

from abc import ABC, abstractmethod
from inspect import signature
from types import MethodType
from typing import Callable

from bobocep import BoboError
from bobocep.cep.event import BoboEvent, BoboHistory


class BoboPredicateError(BoboError):
    """A predicate error."""


class BoboPredicate(ABC):
    """A predicate that evaluates to either True or False."""

    @abstractmethod
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


class BoboPredicateCall(BoboPredicate):
    """A predicate that evaluates using a custom function or method."""

    _EXC_INVALID_PARAM = "call must have {} parameters, found {}"
    _LEN_PARAM_CALL = 2

    def __init__(self, call: Callable):
        super().__init__()

        len_param_call = len(signature(call).parameters)

        if len_param_call != self._LEN_PARAM_CALL:
            raise BoboPredicateError(
                self._EXC_INVALID_PARAM.format(
                    self._LEN_PARAM_CALL,
                    len_param_call))

        self._call = call

        # Prevent garbage collection of object if callable is a method.
        self._obj = call.__self__ if isinstance(call, MethodType) else None

    def evaluate(self, event: BoboEvent, history: BoboHistory) -> bool:
        return self._call(event, history)


class BoboPredicateCallType(BoboPredicateCall):
    """A predicate that evaluates using a custom function or method after
       first checking whether the event data is an instance of a given type.
       If it is not, then a cast to the type can be attempted and a copy of
       the event is passed with its data cast to the type. Note that the
       copy is only used within the predicate, and the original event remains
       in use elsewhere."""

    def __init__(self,
                 call: Callable,
                 dtype: type,
                 subtype: bool = True,
                 cast: bool = True):
        super().__init__(call=call)

        self._dtype: type = dtype
        self._subtype: bool = subtype
        self._cast: bool = cast

    def evaluate(self, event: BoboEvent, history: BoboHistory) -> bool:
        ok_type: bool = True

        if self._subtype:
            # Checking type and subtypes
            if not isinstance(event.data, self._dtype):
                ok_type = False
        else:
            # Checking exact type only
            if not type(event.data) == self._dtype:
                ok_type = False

        if not ok_type:
            if self._cast:
                # Type does not match, attempting cast
                try:
                    event = event.cast(self._dtype)

                except (TypeError, ValueError):
                    # Cast failed
                    return False
            else:
                # Not attempting cast
                return False

        # Type match or successful cast
        return self._call(event, history)
