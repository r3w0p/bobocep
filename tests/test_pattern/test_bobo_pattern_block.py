# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

import pytest
from dpcontracts import PreconditionError

from bobocep.pattern.bobo_pattern_block import BoboPatternBlock
from bobocep.predicate.bobo_predicate_call import BoboPredicateCall


def test_negated_and_optional_both_false_if_loop_true():
    assert type(BoboPatternBlock(
        group="group",
        predicates=[BoboPredicateCall(call=lambda e, h: True)],
        strict=False,
        loop=True,
        negated=False,
        optional=False
    )) is BoboPatternBlock


def test_negated_and_optional_both_true_if_loop_true():
    with pytest.raises(PreconditionError):
        BoboPatternBlock(
            group="group",
            predicates=[BoboPredicateCall(call=lambda e, h: True)],
            strict=False,
            loop=True,
            negated=True,
            optional=True
        )


def test_negated_true_optional_false_if_loop_true():
    with pytest.raises(PreconditionError):
        BoboPatternBlock(
            group="group",
            predicates=[BoboPredicateCall(call=lambda e, h: True)],
            strict=False,
            loop=True,
            negated=True,
            optional=False
        )


def test_negated_false_optional_true_if_loop_true():
    with pytest.raises(PreconditionError):
        BoboPatternBlock(
            group="group",
            predicates=[BoboPredicateCall(call=lambda e, h: True)],
            strict=False,
            loop=True,
            negated=False,
            optional=True
        )


def test_negated_and_optional_both_false_if_loop_false():
    assert type(BoboPatternBlock(
        group="group",
        predicates=[BoboPredicateCall(call=lambda e, h: True)],
        strict=False,
        loop=False,
        negated=False,
        optional=False
    )) is BoboPatternBlock


def test_negated_and_optional_both_true_if_loop_false():
    with pytest.raises(PreconditionError):
        BoboPatternBlock(
            group="group",
            predicates=[BoboPredicateCall(call=lambda e, h: True)],
            strict=False,
            loop=False,
            negated=True,
            optional=True
        )


def test_negated_true_optional_false_if_loop_false():
    assert type(BoboPatternBlock(
        group="group",
        predicates=[BoboPredicateCall(call=lambda e, h: True)],
        strict=False,
        loop=False,
        negated=True,
        optional=False
    )) is BoboPatternBlock


def test_negated_false_optional_true_if_loop_false():
    assert type(BoboPatternBlock(
        group="group",
        predicates=[BoboPredicateCall(call=lambda e, h: True)],
        strict=False,
        loop=False,
        negated=False,
        optional=True
    )) is BoboPatternBlock
