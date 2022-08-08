# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from datetime import datetime

import pytest

from bobocep.event.bobo_event_action import BoboEventAction
from bobocep.event.bobo_event_error import BoboEventError


class TestInvalid:

    def test_process_name_length_0(self):
        with pytest.raises(BoboEventError):
            BoboEventAction(
                event_id="event_id",
                timestamp=datetime.now(),
                data=None,
                process_name="",
                pattern_name="pattern",
                action_name="action",
                success=True)

    def test_pattern_name_length_0(self):
        with pytest.raises(BoboEventError):
            BoboEventAction(
                event_id="event_id",
                timestamp=datetime.now(),
                data=None,
                process_name="process",
                pattern_name="",
                action_name="action",
                success=True)

    def test_action_name_length_0(self):
        with pytest.raises(BoboEventError):
            BoboEventAction(
                event_id="event_id",
                timestamp=datetime.now(),
                data=None,
                process_name="process",
                pattern_name="pattern",
                action_name="",
                success=True)
