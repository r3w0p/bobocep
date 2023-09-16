# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

from bobocep.cep.phenom.phenom import BoboPhenomenonError, BoboPhenomenon
from tests.test_bobocep.test_cep.test_action import BoboActionTrue
from tests.test_bobocep.test_cep.test_phenom import tc_phenomenon, tc_pattern


class TestValid:

    def test_one_pattern(self):
        name_phenom = "name_phenom"
        name_pattern = "name_pattern"
        name_action = "name_action"

        pattern = tc_pattern(name_pattern)
        action = BoboActionTrue(name_action)
        datagen = lambda p, h: 123
        retain = True

        phenom = BoboPhenomenon(
            name=name_phenom,
            patterns=[pattern],
            action=action,
            datagen=datagen,
            retain=retain)

        assert phenom.name == name_phenom
        assert len(phenom.patterns) == 1
        assert phenom.patterns[0].name == name_pattern
        assert phenom.action is not None
        assert phenom.action.name == name_action
        assert phenom.datagen is not None
        assert phenom.datagen(None, None) == 123
        assert phenom.retain


class TestInvalid:

    def test_name_length_0(self):
        with pytest.raises(BoboPhenomenonError):
            tc_phenomenon(name="")

    def test_datagen_too_few_parameters(self):
        with pytest.raises(BoboPhenomenonError):
            tc_phenomenon(datagen=lambda p: None)

    def test_datagen_too_many_parameters(self):
        with pytest.raises(BoboPhenomenonError):
            tc_phenomenon(datagen=lambda p, h, a: None)
