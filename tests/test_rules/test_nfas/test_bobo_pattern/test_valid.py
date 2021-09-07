import pytest
from bobocep.rules.nfas.bobo_pattern import BoboPattern
from bobocep.rules.nfas.bobo_pattern import BoboPatternLayer
from bobocep.rules.predicates.bobo_predicate_callable import BoboPredicateCallable


def test_valid_start_only():
    test_pattern = BoboPattern()
    test_group = "test_group_start"
    test_predicate = BoboPredicateCallable(call=lambda e, h: True)

    test_pattern.start(
        group=test_group,
        predicate=test_predicate
    )

    assert len(test_pattern.layers) == 1
    layer_start = test_pattern.layers[0]

    assert layer_start.group == test_group
    assert len(layer_start.predicates) == 1
    assert layer_start.predicates[0] == test_predicate
    assert layer_start.times == 1
    assert layer_start.loop is False
    assert layer_start.strict is False
    assert layer_start.negated is False
    assert layer_start.optional is False


def test_valid_start_next():
    test_pattern = BoboPattern()
    test_pattern.start(
        group="test_group_start",
        predicate=BoboPredicateCallable(call=lambda e, h: True)
    )

    test_group = "test_group_next"
    test_predicate = BoboPredicateCallable(call=lambda e, h: True)
    test_times = 3
    test_loop = False
    test_optional = False

    test_pattern.next(
        group=test_group,
        predicate=test_predicate,
        times=test_times,
        loop=test_loop,
        optional=test_optional
    )

    assert len(test_pattern.layers) == 2
    layer_next = test_pattern.layers[1]

    assert layer_next.group == test_group
    assert len(layer_next.predicates) == 1
    assert layer_next.predicates[0] == test_predicate
    assert layer_next.times == test_times
    assert layer_next.loop is test_loop
    assert layer_next.strict is True
    assert layer_next.negated is False
    assert layer_next.optional is test_optional


def test_valid_start_not_next():
    test_pattern = BoboPattern()
    test_pattern.start(
        group="test_group_start",
        predicate=BoboPredicateCallable(call=lambda e, h: True)
    )

    test_group = "test_group_not_next"
    test_predicate = BoboPredicateCallable(call=lambda e, h: True)

    test_pattern.not_next(
        group=test_group,
        predicate=test_predicate
    )

    assert len(test_pattern.layers) == 2
    layer_not_next = test_pattern.layers[1]

    assert layer_not_next.group == test_group
    assert len(layer_not_next.predicates) == 1
    assert layer_not_next.predicates[0] == test_predicate
    assert layer_not_next.times == 1
    assert layer_not_next.loop is False
    assert layer_not_next.strict is True
    assert layer_not_next.negated is True
    assert layer_not_next.optional is False


def test_valid_start_followed_by():
    test_pattern = BoboPattern()
    test_pattern.start(
        group="test_group_start",
        predicate=BoboPredicateCallable(call=lambda e, h: True)
    )

    test_group = "test_group_followed_by"
    test_predicate = BoboPredicateCallable(call=lambda e, h: True)
    test_times = 3
    test_loop = False
    test_optional = False

    test_pattern.followed_by(
        group=test_group,
        predicate=test_predicate,
        times=test_times,
        loop=test_loop,
        optional=test_optional
    )

    assert len(test_pattern.layers) == 2
    layer_followed_by = test_pattern.layers[1]

    assert layer_followed_by.group == test_group
    assert len(layer_followed_by.predicates) == 1
    assert layer_followed_by.predicates[0] == test_predicate
    assert layer_followed_by.times == test_times
    assert layer_followed_by.loop is test_loop
    assert layer_followed_by.strict is False
    assert layer_followed_by.negated is False
    assert layer_followed_by.optional is test_optional


def test_valid_start_not_followed_by():
    test_pattern = BoboPattern()
    test_pattern.start(
        group="test_group_start",
        predicate=BoboPredicateCallable(call=lambda e, h: True)
    )

    test_group = "test_group_not_followed_by"
    test_predicate = BoboPredicateCallable(call=lambda e, h: True)

    test_pattern.not_followed_by(
        group=test_group,
        predicate=test_predicate
    )

    assert len(test_pattern.layers) == 2
    layer_not_followed_by = test_pattern.layers[1]

    assert layer_not_followed_by.group == test_group
    assert len(layer_not_followed_by.predicates) == 1
    assert layer_not_followed_by.predicates[0] == test_predicate
    assert layer_not_followed_by.times == 1
    assert layer_not_followed_by.loop is False
    assert layer_not_followed_by.strict is False
    assert layer_not_followed_by.negated is True
    assert layer_not_followed_by.optional is False


def test_valid_start_followed_by_any():
    test_pattern = BoboPattern()
    test_pattern.start(
        group="test_group_start",
        predicate=BoboPredicateCallable(call=lambda e, h: True)
    )

    test_group = "test_group_followed_by_any"
    test_predicates = [
        BoboPredicateCallable(call=lambda e, h: True),
        BoboPredicateCallable(call=lambda e, h: True),
        BoboPredicateCallable(call=lambda e, h: True)
    ]

    test_pattern.followed_by_any(
        group=test_group,
        predicates=test_predicates
    )

    assert len(test_pattern.layers) == 2
    layer_followed_by_any = test_pattern.layers[1]

    assert layer_followed_by_any.group == test_group
    assert len(layer_followed_by_any.predicates) == 3
    assert layer_followed_by_any.predicates == test_predicates
    assert layer_followed_by_any.times == 1
    assert layer_followed_by_any.loop is False
    assert layer_followed_by_any.strict is False
    assert layer_followed_by_any.negated is False
    assert layer_followed_by_any.optional is False


def test_valid_precondition():
    test_pattern = BoboPattern()
    test_predicate = BoboPredicateCallable(call=lambda e, h: True)

    test_pattern.precondition(predicate=test_predicate)

    assert len(test_pattern.preconditions) == 1
    assert test_pattern.preconditions[0] == test_predicate


def test_valid_haltcondition():
    test_pattern = BoboPattern()
    test_predicate = BoboPredicateCallable(call=lambda e, h: True)

    test_pattern.haltcondition(predicate=test_predicate)

    assert len(test_pattern.haltconditions) == 1
    assert test_pattern.haltconditions[0] == test_predicate
