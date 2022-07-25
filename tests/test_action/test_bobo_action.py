# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

from bobocep.action.bobo_action import BoboAction
from bobocep.action.bobo_action_error import BoboActionError
from bobocep.action.bobo_action_response import \
    BoboActionResponse
from bobocep.event.bobo_event_complex import BoboEventComplex


class BoboActionTrue(BoboAction):

    def execute(self, event: BoboEventComplex) -> BoboActionResponse:
        return BoboActionResponse(action_name=self.name, success=True)


class TestInvalid:

    def test_name_length_0(self):
        with pytest.raises(BoboActionError):
            BoboActionTrue(name="")
