# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

from bobocep.process.bobo_process import BoboProcess
from bobocep.process.bobo_process_error import BoboProcessError
from bobocep.process.pattern.bobo_pattern import BoboPattern
from bobocep.process.pattern.bobo_pattern_block import BoboPatternBlock
from bobocep.process.pattern.predicate.bobo_predicate_call import \
    BoboPredicateCall


def _pattern_minimum(name: str = "pattern", group: str = "group"):
    return BoboPattern(
        name=name,
        blocks=[BoboPatternBlock(
            group=group,
            predicates=[BoboPredicateCall(call=lambda e, h: None)],
            strict=False,
            loop=False,
            negated=False,
            optional=False)],
        preconditions=[BoboPredicateCall(call=lambda e, h: None)],
        haltconditions=[BoboPredicateCall(call=lambda e, h: None)])


class TestInvalid:

    def test_name_length_0(self):
        with pytest.raises(BoboProcessError):
            BoboProcess(
                name="",
                patterns=[_pattern_minimum()],
                datagen=lambda p, h: None,
                action=None,
                retain=True)

    def test_datagen_too_few_parameters(self):
        with pytest.raises(BoboProcessError):
            BoboProcess(
                name="process_name",
                patterns=[_pattern_minimum()],
                datagen=lambda p: None,
                action=None,
                retain=True)

    def test_datagen_too_many_parameters(self):
        with pytest.raises(BoboProcessError):
            BoboProcess(
                name="process_name",
                patterns=[_pattern_minimum()],
                datagen=lambda p, h, a: None,
                action=None,
                retain=True)
