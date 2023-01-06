# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from json import loads

from bobocep.cep.event.bobo_event import BoboEvent
from bobocep.cep.event.bobo_event_action import BoboEventAction
from bobocep.cep.event.bobo_event_complex import BoboEventComplex
from bobocep.cep.event.bobo_event_simple import BoboEventSimple
from bobocep.misc.bobo_jsonable_error import BoboJSONableError


class BoboEventFactory:
    """An event factory that instantiates a BoboEvent from a JSON string
    representation of one."""

    @staticmethod
    def from_json_str(j: str) -> BoboEvent:
        d: dict = loads(j)

        if BoboEvent.EVENT_TYPE not in d:
            raise BoboJSONableError(
                "Missing key '{}'.".format(BoboEvent.EVENT_TYPE))

        if d[BoboEvent.EVENT_TYPE] == BoboEventAction.TYPE_ACTION:
            return BoboEventAction.from_dict(d)

        if d[BoboEvent.EVENT_TYPE] == BoboEventComplex.TYPE_COMPLEX:
            return BoboEventComplex.from_dict(d)

        if d[BoboEvent.EVENT_TYPE] == BoboEventSimple.TYPE_SIMPLE:
            return BoboEventSimple.from_dict(d)

        raise BoboJSONableError(
            "Unknown event type '{}'.".format(d[BoboEvent.EVENT_TYPE]))
