# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

import tests.common as tc
from bobocep.cep.event import BoboEventError


class TestInvalid:

    def test_event_id_length_0(self):
        with pytest.raises(BoboEventError):
            tc.event_simple(event_id="")
