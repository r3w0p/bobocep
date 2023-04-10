# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest


# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from bobocep.cep.phenomenon.pattern.builder import BoboPatternBuilder, \
    BoboPatternBuilderError
from bobocep.cep.phenomenon.pattern.predicate import BoboPredicateCall


class TestInvalid:

    def test_name_length_0(self):
        with pytest.raises(BoboPatternBuilderError):
            BoboPatternBuilder(name="")
