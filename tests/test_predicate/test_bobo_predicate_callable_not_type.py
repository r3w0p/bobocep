# Copyright (c) The BoboCEP Authors
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License v3.0.

from datetime import datetime

from bobocep.events.bobo_event_primitive import BoboEventPrimitive
from bobocep.events.bobo_history import BoboHistory
from bobocep.predicate.bobo_predicate_callable_not_type import \
    BoboPredicateCallableNotType


class TestSuperclass:
    def __init__(self):
        super().__init__()


class TestSubclass(TestSuperclass):
    def __init__(self):
        super().__init__()


def test_3_types_int_str_bool_subtype_true_evaluate_invalid():
    predicate = BoboPredicateCallableNotType(
        call=lambda e, h: True, types=[int, str, bool])

    event_1 = BoboEventPrimitive(
        event_id="id_1", timestamp=datetime.now(), data=123)
    event_2 = BoboEventPrimitive(
        event_id="id_2", timestamp=datetime.now(), data="abc")
    event_3 = BoboEventPrimitive(
        event_id="id_3", timestamp=datetime.now(), data=False)

    history = BoboHistory(events={})

    assert not predicate.evaluate(event=event_1, history=history)
    assert not predicate.evaluate(event=event_2, history=history)
    assert not predicate.evaluate(event=event_3, history=history)


def test_3_types_none_float_subtype_true_evaluate_valid():
    predicate = BoboPredicateCallableNotType(
        call=lambda e, h: True, types=[int, str, bool])

    event_1 = BoboEventPrimitive(
        event_id="id_1", timestamp=datetime.now(), data=None)
    event_2 = BoboEventPrimitive(
        event_id="id_2", timestamp=datetime.now(), data=123.4)

    history = BoboHistory(events={})

    assert predicate.evaluate(event=event_1, history=history)
    assert predicate.evaluate(event=event_2, history=history)


def test_superclass_subtype_true_evaluate():
    predicate = BoboPredicateCallableNotType(
        call=lambda e, h: True, types=[TestSuperclass])

    event_1 = BoboEventPrimitive(
        event_id="id_1", timestamp=datetime.now(), data=TestSuperclass())
    event_2 = BoboEventPrimitive(
        event_id="id_2", timestamp=datetime.now(), data=TestSubclass())

    history = BoboHistory(events={})

    assert not predicate.evaluate(event=event_1, history=history)
    assert not predicate.evaluate(event=event_2, history=history)


def test_superclass_subtype_false_evaluate():
    predicate = BoboPredicateCallableNotType(
        call=lambda e, h: True, types=[TestSuperclass], subtype=False)

    event_1 = BoboEventPrimitive(
        event_id="id_1", timestamp=datetime.now(), data=TestSuperclass())
    event_2 = BoboEventPrimitive(
        event_id="id_2", timestamp=datetime.now(), data=TestSubclass())

    history = BoboHistory(events={})

    assert not predicate.evaluate(event=event_1, history=history)
    assert predicate.evaluate(event=event_2, history=history)
