# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from json import dumps
from typing import Any, Tuple

import pytest

from bobocep.cep.event import BoboEventAction, BoboEvent, BoboEventFactory, \
    BoboEventSimple, BoboHistory, BoboEventComplex, BoboEventError
from tests.test_bobocep.test_cep.test_event import tc_event_simple


class TestValid:

    def test_generate_action_data_int(self):
        event_id: str = "event_id"
        timestamp: int = 123456789
        data: Any = 123
        phenom_name: str = "phenom_name"
        pattern_name: str = "pattern_name"
        action_name: str = "action_name"
        success: bool = True

        j_action: str = dumps({
            BoboEventAction.EVENT_TYPE: BoboEventAction.TYPE_ACTION,
            BoboEventAction.EVENT_ID: event_id,
            BoboEventAction.TIMESTAMP: timestamp,
            BoboEventAction.DATA: data,
            BoboEventAction.PHENOMENON_NAME: phenom_name,
            BoboEventAction.PATTERN_NAME: pattern_name,
            BoboEventAction.ACTION_NAME: action_name,
            BoboEventAction.SUCCESS: success
        })

        event: BoboEvent = BoboEventFactory.from_json_str(j_action)

        assert isinstance(event, BoboEventAction)
        assert event.event_id == event_id
        assert event.timestamp == timestamp
        assert event.data == data
        assert event.phenomenon_name == phenom_name
        assert event.pattern_name == pattern_name
        assert event.action_name == action_name
        assert event.success == success

    def test_generate_complex_data_int_history_one_event(self):
        event_id: str = "event_id"
        timestamp: int = 123456789
        data: Any = 123
        phenom_name: str = "phenom_name"
        pattern_name: str = "pattern_name"

        group_history: str = "group_history"
        event_history: BoboEventSimple = tc_event_simple()
        history: BoboHistory = BoboHistory(events={
            group_history: [event_history]
        })

        j_complex: str = dumps({
            BoboEventComplex.EVENT_TYPE: BoboEventComplex.TYPE_COMPLEX,
            BoboEventComplex.EVENT_ID: event_id,
            BoboEventComplex.TIMESTAMP: timestamp,
            BoboEventComplex.DATA: data,
            BoboEventComplex.PHENOMENON_NAME: phenom_name,
            BoboEventComplex.PATTERN_NAME: pattern_name,
            BoboEventComplex.HISTORY: history
        }, default=lambda o: o.to_json_str())

        event: BoboEvent = BoboEventFactory.from_json_str(j_complex)

        assert isinstance(event, BoboEventComplex)
        assert event.event_id == event_id
        assert event.timestamp == timestamp
        assert event.data == data
        assert event.phenomenon_name == phenom_name
        assert event.pattern_name == pattern_name
        assert isinstance(event.history, BoboHistory)

        group: Tuple[BoboEvent, ...] = event.history.group(group_history)
        assert len(group) == 1
        assert isinstance(group[0], BoboEventSimple)
        assert group[0].event_id == event_history.event_id
        assert group[0].timestamp == event_history.timestamp
        assert group[0].data == event_history.data

    def test_generate_simple_data_int(self):
        event_id: str = "event_id"
        timestamp: int = 123456789
        data: Any = 123

        j_simple: str = dumps({
            BoboEventSimple.EVENT_TYPE: BoboEventSimple.TYPE_SIMPLE,
            BoboEventSimple.EVENT_ID: event_id,
            BoboEventSimple.TIMESTAMP: timestamp,
            BoboEventSimple.DATA: data
        })

        event: BoboEvent = BoboEventFactory.from_json_str(j_simple)

        assert isinstance(event, BoboEventSimple)
        assert event.event_id == event_id
        assert event.timestamp == timestamp
        assert event.data == data


class TestInvalid:

    def test_no_event_type(self):
        j_invalid: str = dumps({
            BoboEventSimple.EVENT_ID: "event_id",
            BoboEventSimple.TIMESTAMP: 123456789,
            BoboEventSimple.DATA: 123
        })

        with pytest.raises(BoboEventError):
            BoboEventFactory.from_json_str(j_invalid)

    def test_unknown_event_type(self):
        j_invalid: str = dumps({
            BoboEventSimple.EVENT_TYPE: "unknown",
            BoboEventSimple.EVENT_ID: "event_id",
            BoboEventSimple.TIMESTAMP: 123456789,
            BoboEventSimple.DATA: 123
        })

        with pytest.raises(BoboEventError):
            BoboEventFactory.from_json_str(j_invalid)
