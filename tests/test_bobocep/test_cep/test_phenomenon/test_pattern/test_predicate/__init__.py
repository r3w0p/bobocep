from typing import Callable

from bobocep.cep.phenomenon.pattern.predicate import BoboPredicateCall


def tc_predicate(call: Callable = lambda e, h: True):
    return BoboPredicateCall(call=call)  #
