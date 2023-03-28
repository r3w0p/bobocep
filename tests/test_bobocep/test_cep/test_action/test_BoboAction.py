# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

from bobocep.cep.action.action import BoboActionError
from tests.test_bobocep.test_cep.test_action import BoboActionTrue


class TestInvalid:

    def test_name_length_0(self):
        with pytest.raises(BoboActionError):
            BoboActionTrue(name="")
