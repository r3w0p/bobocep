# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest
import tests.common as tc
from bobocep.cep.event.bobo_event_simple import BoboEventSimple


class TestValid:

    def test_to_str(self):
        event = tc.event_simple()
        assert event.__str__() == event.to_json_str()

    def test_to_from_json_str(self):
        event_original = tc.event_simple(data=123)
        json_event = event_original.to_json_str()
        event_new = BoboEventSimple.from_json_str(json_event)

        assert event_original.event_id == event_new.event_id
        assert event_original.timestamp == event_new.timestamp
        assert event_original.data == event_new.data

    def test_cast_str_to_int(self):
        event = tc.event_simple(data="123")
        assert type(event.data) == str

        event_cast = event.cast(int)
        assert type(event_cast.data) == int
