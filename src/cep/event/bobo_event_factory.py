# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from src.cep.event.bobo_event import BoboEvent
from src.cep.event.bobo_event_action import BoboEventAction
from src.cep.event.bobo_event_complex import BoboEventComplex
from src.cep.event.bobo_event_simple import BoboEventSimple
from src.cep.misc.bobo_serializable_error import BoboSerializableError


class BoboEventFactory:
    """An event factory."""

    @staticmethod
    def from_json(d: dict) -> BoboEvent:
        if BoboEvent.EVENT_TYPE not in d:
            raise BoboSerializableError(
                "Missing key '{}'.".format(BoboEvent.EVENT_TYPE))

        if d[BoboEvent.EVENT_TYPE] == BoboEventAction.__class__.__name__:
            return BoboEventAction.from_dict(d)

        if d[BoboEvent.EVENT_TYPE] == BoboEventComplex.__class__.__name__:
            return BoboEventComplex.from_dict(d)

        if d[BoboEvent.EVENT_TYPE] == BoboEventSimple.__class__.__name__:
            return BoboEventSimple.from_dict(d)

        raise BoboSerializableError(
            "Unknown event type '{}'.".format(d[BoboEvent.EVENT_TYPE]))
