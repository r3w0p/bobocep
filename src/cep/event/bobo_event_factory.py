# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from src.cep.event.bobo_event import BoboEvent
from src.cep.event.bobo_event_action import BoboEventAction
from src.cep.event.bobo_event_complex import BoboEventComplex
from src.cep.event.bobo_event_simple import BoboEventSimple
from src.misc.bobo_jsonable_error import BoboJSONableError


class BoboEventFactory:
    """An event factory."""

    @staticmethod
    def from_json(d: dict) -> BoboEvent:
        if BoboEvent.EVENT_TYPE not in d:
            raise BoboJSONableError(
                "Missing key '{}'.".format(BoboEvent.EVENT_TYPE))

        if d[BoboEvent.EVENT_TYPE] == BoboEventAction.TYPE_ACTION:
            return BoboEventAction.from_json_str(d)

        if d[BoboEvent.EVENT_TYPE] == BoboEventComplex.TYPE_COMPLEX:
            return BoboEventComplex.from_json_str(d)

        if d[BoboEvent.EVENT_TYPE] == BoboEventSimple.TYPE_SIMPLE:
            return BoboEventSimple.from_json_str(d)

        raise BoboJSONableError(
            "Unknown event type '{}'.".format(d[BoboEvent.EVENT_TYPE]))
