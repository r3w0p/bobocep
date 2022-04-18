from datetime import datetime

from bobocep.events.bobo_event_primitive import BoboEventPrimitive
from bobocep.events.bobo_history import BoboHistory
from bobocep.predicate.bobo_predicate_callable_type import \
    BoboPredicateCallableType


def test_3_types_3_events_evaluate_valid():
    predicate = BoboPredicateCallableType(
        call=lambda e, h: True, types=[int, str, bool])

    event_int = BoboEventPrimitive(
        event_id="id", timestamp=datetime.now(), data=123)
    event_str = BoboEventPrimitive(
        event_id="id", timestamp=datetime.now(), data="abc")
    event_bool = BoboEventPrimitive(
        event_id="id", timestamp=datetime.now(), data=False)

    history = BoboHistory(events={})

    assert predicate.evaluate(event=event_int, history=history)
    assert predicate.evaluate(event=event_str, history=history)
    assert predicate.evaluate(event=event_bool, history=history)


def test_3_types_2_events_evaluate_invalid():
    predicate = BoboPredicateCallableType(
        call=lambda e, h: True, types=[int, str, bool])

    event_none = BoboEventPrimitive(
        event_id="id", timestamp=datetime.now(), data=None)
    event_float = BoboEventPrimitive(
        event_id="id", timestamp=datetime.now(), data=123.4)

    history = BoboHistory(events={})

    assert not predicate.evaluate(event=event_none, history=history)
    assert not predicate.evaluate(event=event_float, history=history)
