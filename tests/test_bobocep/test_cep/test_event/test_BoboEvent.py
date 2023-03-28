# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

from bobocep.cep.event import BoboEventError
from tests.test_bobocep.test_cep.test_event import tc_event_simple


class TestInvalid:

    def test_event_id_length_0(self):
        with pytest.raises(BoboEventError):
            tc_event_simple(event_id="")
