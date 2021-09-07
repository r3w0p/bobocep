import pytest

from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.bobo_history import BoboHistory
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.rules.predicates.bobo_predicate_callable import \
    BoboPredicateCallable
from bobocep.rules.nfas.bobo_pattern_layer import BoboPatternLayer


def predicate_callable_function(event: BoboEvent, history: BoboHistory):
    return True


def test_valid_arguments():
    test_group = "test_group"
    test_predicates = [
        BoboPredicateCallable(call=predicate_callable_function)
    ]
    test_times = 1
    test_loop = False
    test_strict = False
    test_negated = False
    test_optional = False

    test_pattern_layer = BoboPatternLayer(
        group=test_group,
        predicates=test_predicates,
        times=test_times,
        loop=test_loop,
        strict=test_strict,
        negated=test_negated,
        optional=test_optional
    )

    assert test_pattern_layer.group == test_group
    assert test_pattern_layer.predicates == test_predicates
    assert test_pattern_layer.times == test_times
    assert test_pattern_layer.loop == test_loop
    assert test_pattern_layer.strict == test_strict
    assert test_pattern_layer.negated == test_negated
    assert test_pattern_layer.optional == test_optional
