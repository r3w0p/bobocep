# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

from bobocep.cep.event import BoboEventAction, BoboEventError
from bobocep.cep.gen.timestamp import BoboGenTimestampEpoch
from tests.test_bobocep.test_cep.test_event import tc_event_action


class TestValid:

    def test_to_str(self):
        event = tc_event_action()
        assert event.__str__() == event.to_json_str()

    def test_to_from_json_str(self):
        event_original = tc_event_action(data=123)
        json_event = event_original.to_json_str()
        event_new = BoboEventAction.from_json_str(json_event)

        assert event_original.event_id == event_new.event_id
        assert event_original.timestamp == event_new.timestamp
        assert event_original.data == event_new.data
        assert event_original.phenomenon_name == event_new.phenomenon_name
        assert event_original.pattern_name == event_new.pattern_name
        assert event_original.action_name == event_new.action_name
        assert event_original.success == event_new.success

    def test_cast_str_to_int(self):
        event = tc_event_action(data="123")
        assert type(event.data) == str

        event_cast = event.cast(int)
        assert type(event_cast.data) == int


class TestInvalid:

    def test_event_id_length_0(self):
        with pytest.raises(BoboEventError):
            BoboEventAction(
                event_id="",
                timestamp=BoboGenTimestampEpoch().generate(),
                data=None,
                phenomenon_name="phenomenon",
                pattern_name="pattern",
                action_name="action",
                success=True)

    def test_phenomenon_name_length_0(self):
        with pytest.raises(BoboEventError):
            BoboEventAction(
                event_id="event_id",
                timestamp=BoboGenTimestampEpoch().generate(),
                data=None,
                phenomenon_name="",
                pattern_name="pattern",
                action_name="action",
                success=True)

    def test_pattern_name_length_0(self):
        with pytest.raises(BoboEventError):
            BoboEventAction(
                event_id="event_id",
                timestamp=BoboGenTimestampEpoch().generate(),
                data=None,
                phenomenon_name="phenomenon",
                pattern_name="",
                action_name="action",
                success=True)

    def test_action_name_length_0(self):
        with pytest.raises(BoboEventError):
            BoboEventAction(
                event_id="event_id",
                timestamp=BoboGenTimestampEpoch().generate(),
                data=None,
                phenomenon_name="phenomenon",
                pattern_name="pattern",
                action_name="",
                success=True)
