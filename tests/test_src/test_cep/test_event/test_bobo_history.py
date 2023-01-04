# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from time import sleep

from bobocep.cep.event.bobo_event_simple import BoboEventSimple
from bobocep.cep.event.bobo_history import BoboHistory
from bobocep.cep.gen.timestamp.bobo_gen_timestamp_epoch import \
    BoboGenTimestampEpoch


class TestValid:

    def test_empty_history(self):
        history = BoboHistory(events={})

        assert history.all() == tuple()
        assert history.first() is None
        assert history.last() is None

    def test_1_group_1_event(self):
        group = "group"
        event = BoboEventSimple(
            event_id="1", timestamp=BoboGenTimestampEpoch().generate(),
            data=True)

        history = BoboHistory(events={group: [event]})

        assert history.all() == (event,)
        assert history.group(group=group) == (event,)
        assert history.first() == event
        assert history.last() == event

    def test_first_last_2_groups_2_events(self):
        timegen = BoboGenTimestampEpoch()

        group_low = "low"
        group_high = "high"
        event_low = BoboEventSimple(
            event_id="1", timestamp=timegen.generate(), data=True)
        sleep(0.2)
        event_high = BoboEventSimple(
            event_id="2", timestamp=timegen.generate(), data=True)

        history = BoboHistory(events={
            group_low: [event_low],
            group_high: [event_high]
        })

        assert history.first() == event_low
        assert history.last() == event_high

    def test_group_name_that_does_not_exist(self):
        history = BoboHistory(events={})

        assert history.group(group="group") == tuple()
