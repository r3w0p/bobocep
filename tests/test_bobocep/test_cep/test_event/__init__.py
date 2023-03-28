from typing import Optional

from bobocep.cep.event import BoboEventSimple, BoboHistory, BoboEventComplex, \
    BoboEventAction
from bobocep.cep.gen.event_id import BoboGenEventIDUnique
from bobocep.cep.gen.timestamp import BoboGenTimestampEpoch


class BoboEventSimpleSubclass(BoboEventSimple):
    """"""


def tc_event_simple(event_id: Optional[str] = None,
                    timestamp: Optional[int] = None,
                    data=None):
    return BoboEventSimple(
        event_id=event_id if event_id is not None else
        BoboGenEventIDUnique().generate(),
        timestamp=timestamp if timestamp is not None else
        BoboGenTimestampEpoch().generate(),
        data=data)


def tc_event_complex(event_id: Optional[str] = None,
                     timestamp: Optional[int] = None,
                     data=None,
                     phenomenon_name: str = "phenomenon",
                     pattern_name: str = "pattern",
                     history: Optional[BoboHistory] = None):
    return BoboEventComplex(
        event_id=event_id if event_id is not None else
        BoboGenEventIDUnique().generate(),
        timestamp=timestamp if timestamp is not None else
        BoboGenTimestampEpoch().generate(),
        data=data,
        phenomenon_name=phenomenon_name,
        pattern_name=pattern_name,
        history=history if history is not None else
        BoboHistory(events={}))


def tc_event_action(event_id: Optional[str] = None,
                    timestamp: Optional[int] = None,
                    data=None,
                    phenomenon_name: str = "phenomenon",
                    pattern_name: str = "pattern",
                    action_name: str = "action",
                    success: bool = True):
    return BoboEventAction(
        event_id=event_id if event_id is not None else
        BoboGenEventIDUnique().generate(),
        timestamp=timestamp if timestamp is not None else
        BoboGenTimestampEpoch().generate(),
        data=data,
        phenomenon_name=phenomenon_name,
        pattern_name=pattern_name,
        action_name=action_name,
        success=success)
