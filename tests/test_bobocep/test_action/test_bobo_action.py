# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from datetime import datetime

import pytest

from bobocep.action.bobo_action import BoboAction
from bobocep.action.bobo_action_error import BoboActionError
from bobocep.event.bobo_event_action import BoboEventAction
from bobocep.event.bobo_event_complex import BoboEventComplex


class BoboActionTrue(BoboAction):

    def execute(self, event: BoboEventComplex) -> BoboEventAction:
        return BoboEventAction(
            event_id=event.event_id,
            timestamp=datetime.now(),
            data=True,
            action_name=self.name,
            success=True)


class TestInvalid:

    def test_name_length_0(self):
        with pytest.raises(BoboActionError):
            BoboActionTrue(name="")
