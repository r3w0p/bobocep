# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from typing import Callable, Optional, List

from bobocep.cep.action.action import BoboAction
from bobocep.cep.phenom.pattern.pattern import BoboPattern
from bobocep.cep.phenom.phenom import BoboPhenomenon
from tests.test_bobocep.test_cep.test_phenomenon.test_pattern import tc_pattern


def tc_phenomenon(
        name: str = "phenomenon",
        datagen: Callable = lambda p, h: None,
        patterns: Optional[List[BoboPattern]] = None,
        action: Optional[BoboAction] = None):
    return BoboPhenomenon(
        name=name,
        datagen=datagen,
        patterns=patterns if patterns is not None else [tc_pattern()],
        action=action)
