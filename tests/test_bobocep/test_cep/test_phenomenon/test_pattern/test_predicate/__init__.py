# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from typing import Callable

from bobocep.cep.phenomenon.pattern.predicate import BoboPredicateCall


def tc_predicate(call: Callable = lambda e, h: True):
    return BoboPredicateCall(call=call)  #
