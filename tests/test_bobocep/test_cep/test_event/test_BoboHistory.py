# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from time import sleep

import tests.common as tc
from bobocep.cep.event import BoboHistory, BoboEventSimple
from bobocep.cep.gen.timestamp import BoboGenTimestampEpoch


class TestValid:

    def test_to_str(self):
        history = BoboHistory(events={
            "group": [tc.event_simple(data=123)]
        })
        assert history.__str__() == history.to_json_str()

    def test_to_from_json_str(self):
        group_original = "group"
        event_original = tc.event_simple(data=123)
        history_original = BoboHistory(events={
            group_original: [event_original]
        })
        json_history = history_original.to_json_str()
        history_new = BoboHistory.from_json_str(json_history)

        f_ori = history_original.first()
        f_new = history_new.first()

        assert f_ori is not None
        assert f_new is not None
        assert f_ori.event_id == f_new.event_id
        assert f_ori.timestamp == f_new.timestamp
        assert f_ori.data == f_new.data

        l_ori = history_original.last()
        l_new = history_new.last()

        assert l_ori is not None
        assert l_new is not None
        assert l_ori.event_id == l_new.event_id
        assert l_ori.timestamp == l_new.timestamp
        assert l_ori.data == l_new.data

        g_ori = history_original.group(group_original)
        g_new = history_new.group(group_original)

        assert len(g_ori) == 1
        assert len(g_new) == 1
        assert g_ori[0].event_id == g_new[0].event_id
        assert g_ori[0].timestamp == g_new[0].timestamp
        assert g_ori[0].data == g_new[0].data

        all_ori = history_original.all()
        all_new = history_new.all()

        assert len(all_ori) == 1
        assert len(all_new) == 1
        assert all_ori[0].event_id == all_new[0].event_id
        assert all_ori[0].timestamp == all_new[0].timestamp
        assert all_ori[0].data == all_new[0].data

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
