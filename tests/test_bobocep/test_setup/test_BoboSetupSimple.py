# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

from bobocep.setup import BoboSetupSimple
from tests.test_bobocep.test_cep.test_phenomenon import tc_phenomenon


class TestValid:

    def test_phenomena(self):
        phenomena = [
            tc_phenomenon(name="phenomena_1"),
            tc_phenomenon(name="phenomena_2"),
            tc_phenomenon(name="phenomena_3")
        ]

        setup = BoboSetupSimple(
            phenomena=phenomena)

        engine = setup.generate()
        dec_phenomena = engine.decider.phenomena()
        assert len(dec_phenomena) == 3

        dec_phenomena_names = [dp.name for dp in dec_phenomena]
        assert phenomena[0].name in dec_phenomena_names
        assert phenomena[1].name in dec_phenomena_names
        assert phenomena[2].name in dec_phenomena_names
