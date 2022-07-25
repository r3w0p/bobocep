# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from datetime import datetime

import pytest

from bobocep.action.bobo_action import BoboAction
from bobocep.action.bobo_action_response import BoboActionResponse
from bobocep.action.handler.bobo_action_handler_blocking import \
    BoboActionHandlerBlocking
from bobocep.action.handler.bobo_action_handler_error import \
    BoboActionHandlerError
from bobocep.event.bobo_event_complex import BoboEventComplex
from bobocep.event.bobo_history import BoboHistory
from bobocep.event.event_id.bobo_event_id_unique import BoboEventIDUnique


def _complex():
    return BoboEventComplex(
        event_id=BoboEventIDUnique().generate(),
        timestamp=datetime.now(),
        data=None,
        process_name="process_name",
        pattern_name="pattern_name",
        history=BoboHistory(events={}))


class BoboActionTrue(BoboAction):

    def execute(self, event: BoboEventComplex) -> BoboActionResponse:
        return BoboActionResponse(action_name=self.name, success=True)


class TestValid:

    def test_handle_action(self):
        handler = BoboActionHandlerBlocking(name="handler", max_size=255)

        assert handler.size() == 0
        handler.handle(BoboActionTrue("action_1"), _complex())
        assert handler.size() == 1

    def test_get_response_empty(self):
        handler = BoboActionHandlerBlocking(name="handler", max_size=255)

        assert handler.get_response() is None

    def test_get_response_not_empty(self):
        handler = BoboActionHandlerBlocking(name="handler", max_size=255)

        handler.handle(BoboActionTrue("action_1"), _complex())
        assert handler.get_response() is not None


class TestInvalid:

    def test_name_length_0(self):
        with pytest.raises(BoboActionHandlerError):
            BoboActionHandlerBlocking(
                name="",
                max_size=255)
