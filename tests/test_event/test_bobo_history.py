# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from datetime import datetime

import pytest

from bobocep.event.bobo_event_simple import BoboEventSimple
from bobocep.event.bobo_history import BoboHistory


class TestValid:

    def test_empty_history(self):
        history = BoboHistory(events={})

        assert history.all() == tuple()
        assert history.first() is None
        assert history.last() is None

    def test_1_group_1_event(self):
        group = "group"
        event = BoboEventSimple(
            event_id="1", timestamp=datetime.now(), data=True)

        history = BoboHistory(events={group: [event]})

        assert history.all() == (event,)
        assert history.group(group=group) == (event,)
        assert history.first() == event
        assert history.last() == event

    def test_first_last_2_groups_2_events(self):
        group_low = "low"
        group_high = "high"
        event_low = BoboEventSimple(
            event_id="1", timestamp=datetime.min, data=True)
        event_high = BoboEventSimple(
            event_id="2", timestamp=datetime.max, data=True)

        history = BoboHistory(events={
            group_low: [event_low],
            group_high: [event_high]
        })

        assert history.first() == event_low
        assert history.last() == event_high
