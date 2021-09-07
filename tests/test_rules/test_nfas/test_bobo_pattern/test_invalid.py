import pytest
from bobocep.rules.nfas.bobo_pattern import BoboPattern
from bobocep.rules.nfas.bobo_pattern import BoboPatternLayer
from bobocep.rules.predicates.bobo_predicate_callable import BoboPredicateCallable


def test_invalid_next_before_start():
    test_pattern = BoboPattern()
    test_group = "test_group"
    test_predicate = BoboPredicateCallable(call=lambda e, h: True)

    with pytest.raises(RuntimeError):
        test_pattern.next(
            group=test_group,
            predicate=test_predicate)


def test_invalid_not_next_before_start():
    test_pattern = BoboPattern()
    test_group = "test_group"
    test_predicate = BoboPredicateCallable(call=lambda e, h: True)

    with pytest.raises(RuntimeError):
        test_pattern.not_next(
            group=test_group,
            predicate=test_predicate)


def test_invalid_followed_by_before_start():
    test_pattern = BoboPattern()
    test_group = "test_group"
    test_predicate = BoboPredicateCallable(call=lambda e, h: True)

    with pytest.raises(RuntimeError):
        test_pattern.followed_by(
            group=test_group,
            predicate=test_predicate)


def test_invalid_not_followed_by_before_start():
    test_pattern = BoboPattern()
    test_group = "test_group"
    test_predicate = BoboPredicateCallable(call=lambda e, h: True)

    with pytest.raises(RuntimeError):
        test_pattern.not_followed_by(
            group=test_group,
            predicate=test_predicate)


def test_invalid_followed_by_any_before_start():
    test_pattern = BoboPattern()
    test_group = "test_group"
    test_predicates = [
        BoboPredicateCallable(call=lambda e, h: True),
        BoboPredicateCallable(call=lambda e, h: True),
        BoboPredicateCallable(call=lambda e, h: True)
    ]

    with pytest.raises(RuntimeError):
        test_pattern.followed_by_any(
            group=test_group,
            predicates=test_predicates)
