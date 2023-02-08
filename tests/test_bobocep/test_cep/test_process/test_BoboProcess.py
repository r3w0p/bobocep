# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

import tests.common as tc
from bobocep.cep.phenomenon import BoboPhenomenonError, BoboPhenomenon


class TestInvalid:

    def test_name_length_0(self):
        with pytest.raises(BoboPhenomenonError):
            tc.phenomenon(name="")

    def test_datagen_too_few_parameters(self):
        with pytest.raises(BoboPhenomenonError):
            tc.phenomenon(datagen=lambda p: None)

    def test_datagen_too_many_parameters(self):
        with pytest.raises(BoboPhenomenonError):
            tc.phenomenon(datagen=lambda p, h, a: None)
