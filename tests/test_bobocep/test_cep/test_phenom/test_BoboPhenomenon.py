# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

from bobocep.cep.phenom.phenom import BoboPhenomenonError
from tests.test_bobocep.test_cep.test_phenom import tc_phenomenon


# TODO test valid phenomenon use cases


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
