# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

from bobocep.cep.process.pattern.bobo_pattern_block import BoboPatternBlock
from bobocep.cep.process.pattern.bobo_pattern_block_error import \
    BoboPatternBlockError
from bobocep.cep.process.pattern.predicate.bobo_predicate_call import \
    BoboPredicateCall


class TestValid:

    def test_negated_and_optional_both_false_if_loop_true(self):
        assert type(BoboPatternBlock(
            group="group",
            predicates=[BoboPredicateCall(call=lambda e, h: True)],
            strict=False,
            loop=True,
            negated=False,
            optional=False
        )) is BoboPatternBlock

    def test_negated_and_optional_both_false_if_loop_false(self):
        assert type(BoboPatternBlock(
            group="group",
            predicates=[BoboPredicateCall(call=lambda e, h: True)],
            strict=False,
            loop=False,
            negated=False,
            optional=False
        )) is BoboPatternBlock

    def test_negated_true_optional_false_if_loop_false(self):
        assert type(BoboPatternBlock(
            group="group",
            predicates=[BoboPredicateCall(call=lambda e, h: True)],
            strict=False,
            loop=False,
            negated=True,
            optional=False
        )) is BoboPatternBlock

    def test_negated_false_optional_true_if_loop_false(self):
        assert type(BoboPatternBlock(
            group="group",
            predicates=[BoboPredicateCall(call=lambda e, h: True)],
            strict=False,
            loop=False,
            negated=False,
            optional=True
        )) is BoboPatternBlock


class TestInvalid:

    def test_group_0_length(self):
        with pytest.raises(BoboPatternBlockError):
            BoboPatternBlock(
                group="",
                predicates=[BoboPredicateCall(call=lambda e, h: True)],
                strict=False,
                loop=True,
                negated=False,
                optional=False)

    def test_predicates_0_length(self):
        with pytest.raises(BoboPatternBlockError):
            BoboPatternBlock(
                group="group",
                predicates=[],
                strict=False,
                loop=True,
                negated=False,
                optional=False)

    def test_strict_and_optional_true(self):
        with pytest.raises(BoboPatternBlockError):
            BoboPatternBlock(
                group="group",
                predicates=[BoboPredicateCall(call=lambda e, h: True)],
                strict=True,
                loop=False,
                negated=False,
                optional=True)

    def test_negated_and_optional_true_if_loop_true(self):
        with pytest.raises(BoboPatternBlockError):
            BoboPatternBlock(
                group="group",
                predicates=[BoboPredicateCall(call=lambda e, h: True)],
                strict=False,
                loop=True,
                negated=True,
                optional=True)

    def test_negated_true_optional_false_if_loop_true(self):
        with pytest.raises(BoboPatternBlockError):
            BoboPatternBlock(
                group="group",
                predicates=[BoboPredicateCall(call=lambda e, h: True)],
                strict=False,
                loop=True,
                negated=True,
                optional=False)

    def test_negated_false_optional_true_if_loop_true(self):
        with pytest.raises(BoboPatternBlockError):
            BoboPatternBlock(
                group="group",
                predicates=[BoboPredicateCall(call=lambda e, h: True)],
                strict=False,
                loop=True,
                negated=False,
                optional=True)

    def test_negated_and_optional_true_if_loop_false(self):
        with pytest.raises(BoboPatternBlockError):
            BoboPatternBlock(
                group="group",
                predicates=[BoboPredicateCall(call=lambda e, h: True)],
                strict=False,
                loop=False,
                negated=True,
                optional=True)
