# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from datetime import datetime

from bobocep.event.bobo_event_simple import BoboEventSimple
from bobocep.event.bobo_history import BoboHistory
from bobocep.process.pattern.predicate.bobo_predicate_call_not_type import \
    BoboPredicateCallNotType


class StubSuperclass:
    pass


class StubSubclass(StubSuperclass):
    pass


def test_3_types_int_str_bool_subtype_true_evaluate_invalid():
    predicate = BoboPredicateCallNotType(
        call=lambda e, h: True, types=[int, str, bool])

    event_1 = BoboEventSimple(
        event_id="id_1", timestamp=datetime.now(), data=123)
    event_2 = BoboEventSimple(
        event_id="id_2", timestamp=datetime.now(), data="abc")
    event_3 = BoboEventSimple(
        event_id="id_3", timestamp=datetime.now(), data=False)

    history = BoboHistory(events={})

    assert not predicate.evaluate(event=event_1, history=history)
    assert not predicate.evaluate(event=event_2, history=history)
    assert not predicate.evaluate(event=event_3, history=history)


def test_3_types_none_float_subtype_true_evaluate_valid():
    predicate = BoboPredicateCallNotType(
        call=lambda e, h: True, types=[int, str, bool])

    event_1 = BoboEventSimple(
        event_id="id_1", timestamp=datetime.now(), data=None)
    event_2 = BoboEventSimple(
        event_id="id_2", timestamp=datetime.now(), data=123.4)

    history = BoboHistory(events={})

    assert predicate.evaluate(event=event_1, history=history)
    assert predicate.evaluate(event=event_2, history=history)


def test_superclass_subtype_true_evaluate():
    predicate = BoboPredicateCallNotType(
        call=lambda e, h: True, types=[StubSuperclass])

    event_1 = BoboEventSimple(
        event_id="id_1", timestamp=datetime.now(), data=StubSuperclass())
    event_2 = BoboEventSimple(
        event_id="id_2", timestamp=datetime.now(), data=StubSubclass())

    history = BoboHistory(events={})

    assert not predicate.evaluate(event=event_1, history=history)
    assert not predicate.evaluate(event=event_2, history=history)


def test_superclass_subtype_false_evaluate():
    predicate = BoboPredicateCallNotType(
        call=lambda e, h: True, types=[StubSuperclass], subtype=False)

    event_1 = BoboEventSimple(
        event_id="id_1", timestamp=datetime.now(), data=StubSuperclass())
    event_2 = BoboEventSimple(
        event_id="id_2", timestamp=datetime.now(), data=StubSubclass())

    history = BoboHistory(events={})

    assert not predicate.evaluate(event=event_1, history=history)
    assert predicate.evaluate(event=event_2, history=history)
