# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

import tests.common as tc
from src.cep.action.bobo_action_error import BoboActionError


class TestInvalid:

    def test_name_length_0(self):
        with pytest.raises(BoboActionError):
            tc.BoboActionTrue(name="")
