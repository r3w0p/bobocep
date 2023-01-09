# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest
import tests.common as tc
from bobocep.cep.event.bobo_event import BoboEvent
from bobocep.cep.event.bobo_event_complex import BoboEventComplex
from bobocep.cep.event.bobo_event_simple import BoboEventSimple
from bobocep.cep.event.bobo_history import BoboHistory
from bobocep.cep.process.pattern.predicate.bobo_predicate_call_type import \
    BoboPredicateCallType


class BoboEventSimpleSubclass(BoboEventSimple):
    """"""


class TestValid:

    def test_type_int_no_subtype_no_cast(self):
        predicate = BoboPredicateCallType(
            call=lambda e, h: e.data == 123,
            dtype=int,
            subtype=False,
            cast=False)
        event = tc.event_simple(data=123)
        history = BoboHistory(events={})

        assert predicate.evaluate(event, history)

    def test_type_event_simple_no_subtype_no_cast(self):
        predicate = BoboPredicateCallType(
            call=lambda e, h: e.data.data == 123,
            dtype=BoboEventSimple,
            subtype=False,
            cast=False)
        event = tc.event_simple(data=tc.event_simple(data=123))
        history = BoboHistory(events={})

        assert predicate.evaluate(event, history)

    def test_type_event_subtype_no_cast(self):
        predicate = BoboPredicateCallType(
            call=lambda e, h: e.data.data == 123,
            dtype=BoboEvent,
            subtype=True,
            cast=False)
        event = tc.event_simple(data=tc.event_simple(data=123))
        history = BoboHistory(events={})

        assert predicate.evaluate(event, history)

    def test_type_concrete_superclass_subtype_no_cast(self):
        predicate = BoboPredicateCallType(
            call=lambda e, h: e.data.data == 123,
            dtype=BoboEventSimple,
            subtype=False,
            cast=False)

        event = tc.event_simple(data=BoboEventSimpleSubclass(
            event_id="event_id",
            timestamp=123456789,
            data=123
        ))

        history = BoboHistory(events={})

        assert not predicate.evaluate(event, history)

    def test_type_str_no_subtype_cast_int(self):
        predicate = BoboPredicateCallType(
            call=lambda e, h: e.data == 123,
            dtype=int,
            subtype=False,
            cast=True)
        event = tc.event_simple(data="123")
        history = BoboHistory(events={})

        assert predicate.evaluate(event, history)


class TestInvalid:

    def test_type_abstract_superclass_no_subtype_no_cast(self):
        predicate = BoboPredicateCallType(
            call=lambda e, h: e.data.data == 123,
            dtype=BoboEvent,
            subtype=False,
            cast=False)
        event = tc.event_simple(data=tc.event_simple(data=123))
        history = BoboHistory(events={})

        assert not predicate.evaluate(event, history)

    def test_type_abstract_superclass_subtype_no_cast(self):
        predicate = BoboPredicateCallType(
            call=lambda e, h: e.data.data == 123,
            dtype=BoboEvent,
            subtype=False,
            cast=False)
        event = tc.event_simple(data=tc.event_simple(data=123))
        history = BoboHistory(events={})

        assert not predicate.evaluate(event, history)

    def test_type_concrete_superclass_no_subtype_no_cast(self):
        predicate = BoboPredicateCallType(
            call=lambda e, h: e.data.data == 123,
            dtype=BoboEventSimple,
            subtype=False,
            cast=False)

        event = tc.event_simple(data=BoboEventSimpleSubclass(
            event_id="event_id",
            timestamp=123456789,
            data=123
        ))

        history = BoboHistory(events={})

        assert not predicate.evaluate(event, history)

    def test_type_str_alpha_no_subtype_cast_int(self):
        predicate = BoboPredicateCallType(
            call=lambda e, h: e.data == 123,
            dtype=int,
            subtype=False,
            cast=True)
        event = tc.event_simple(data="abc")
        history = BoboHistory(events={})

        assert not predicate.evaluate(event, history)

    def test_type_int_subtype_no_cast_str(self):
        predicate = BoboPredicateCallType(
            call=lambda e, h: e.data == 123,
            dtype=int,
            subtype=True,
            cast=False)
        event = tc.event_simple(data="abc")
        history = BoboHistory(events={})

        assert not predicate.evaluate(event, history)
