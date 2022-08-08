# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

import tests.common as tc
from bobocep.process.bobo_process import BoboProcess
from bobocep.process.bobo_process_error import BoboProcessError


class TestInvalid:

    def test_name_length_0(self):
        with pytest.raises(BoboProcessError):
            BoboProcess(
                name="",
                patterns=[tc.pattern()],
                datagen=lambda p, h: None,
                action=None,
                retain=True)

    def test_datagen_too_few_parameters(self):
        with pytest.raises(BoboProcessError):
            BoboProcess(
                name="process_name",
                patterns=[tc.pattern()],
                datagen=lambda p: None,
                action=None,
                retain=True)

    def test_datagen_too_many_parameters(self):
        with pytest.raises(BoboProcessError):
            BoboProcess(
                name="process_name",
                patterns=[tc.pattern()],
                datagen=lambda p, h, a: None,
                action=None,
                retain=True)
