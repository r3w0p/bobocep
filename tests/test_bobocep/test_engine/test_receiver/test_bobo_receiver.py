# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from datetime import datetime

import pytest

from bobocep.engine.receiver.bobo_receiver import BoboReceiver
from bobocep.engine.receiver.bobo_receiver_error import BoboReceiverError
from bobocep.engine.receiver.bobo_receiver_subscriber import \
    BoboReceiverSubscriber
from bobocep.engine.receiver.time_event.bobo_time_event import BoboTimeEvent
from bobocep.engine.receiver.time_event.bobo_time_event_elapse import \
    BoboTimeEventElapse
from bobocep.engine.receiver.time_event.bobo_time_event_none import \
    BoboTimeEventNone
from bobocep.engine.receiver.validator.bobo_validator import BoboValidator
from bobocep.engine.receiver.validator.bobo_validator_all import \
    BoboValidatorAll
from bobocep.engine.receiver.validator.bobo_validator_not_type import \
    BoboValidatorNotType
from bobocep.event.bobo_event import BoboEvent
from bobocep.event.bobo_event_complex import BoboEventComplex
from bobocep.event.bobo_event_simple import BoboEventSimple
from bobocep.event.bobo_history import BoboHistory
from bobocep.event.event_id.bobo_event_id import BoboEventID
from bobocep.event.event_id.bobo_event_id_unique import \
    BoboEventIDUnique


def _recsub(validator: BoboValidator = None,
            event_id_gen: BoboEventID = None,
            null_event_gen: BoboTimeEvent = None,
            max_size: int = 255):
    receiver = BoboReceiver(
        validator=validator if validator is not None else
        BoboValidatorAll(),
        event_id_gen=event_id_gen if event_id_gen is not None else
        BoboEventIDUnique(),
        null_event_gen=null_event_gen if null_event_gen is not None else
        BoboTimeEventNone(),
        max_size=max_size)

    subscriber = StubReceiverSubscriber()
    receiver.subscribe(subscriber=subscriber)

    return receiver, subscriber


class StubReceiverSubscriber(BoboReceiverSubscriber):
    def __init__(self):
        super().__init__()
        self.events = []

    def on_receiver_event(self, event: BoboEvent):
        self.events.append(event)


class TestValid:

    def test_size_add_1_event_then_update(self):
        receiver, subscriber = _recsub()

        assert receiver.size() == 0
        receiver.add_data(data=123)
        assert receiver.size() == 1
        receiver.update()
        assert receiver.size() == 0

    def test_subscriber_add_1_event_then_update(self):
        receiver, subscriber = _recsub()

        data = 123
        receiver.add_data(data=data)
        receiver.update()

        assert len(subscriber.events) == 1
        assert isinstance(subscriber.events[0], BoboEventSimple)
        assert subscriber.events[0].data == data

    def test_update_on_queue_empty(self):
        receiver, subscriber = _recsub()

        assert receiver.update() is None

    def test_validator_invalid_data(self):
        receiver, subscriber = _recsub(
            validator=BoboValidatorNotType(types=[type(None)]))

        data = None
        receiver.add_data(data=data)
        receiver.update()

        assert len(subscriber.events) == 0

    def test_null_event(self):
        data_null_event = 456

        receiver, subscriber = _recsub(
            null_event_gen=BoboTimeEventElapse(
                milliseconds=1,
                datagen=lambda: data_null_event,
                from_now=False))

        data = 123
        receiver.add_data(data=data)
        receiver.update()

        assert len(subscriber.events) == 2
        assert isinstance(subscriber.events[0], BoboEventSimple)
        assert isinstance(subscriber.events[1], BoboEventSimple)
        assert subscriber.events[0].data == data
        assert subscriber.events[1].data == data_null_event

    def test_process_add_data_event(self):
        receiver, subscriber = _recsub()

        data_event = 123
        event = BoboEventSimple(
            event_id="1", timestamp=datetime.now(), data=data_event)
        receiver.add_data(data=event)
        receiver.update()

        assert len(subscriber.events) == 1
        assert subscriber.events[0] == event
        assert subscriber.events[0].data == data_event

    def test_on_producer_complex_event(self):
        receiver, subscriber = _recsub()

        event_complex = BoboEventComplex(
            event_id=BoboEventIDUnique().generate(),
            timestamp=datetime.now(),
            data=None,
            process_name="process_1",
            pattern_name="pattern_1",
            history=BoboHistory(events={}))

        assert receiver.size() == 0

        receiver.on_producer_complex_event(event=event_complex)

        assert receiver.size() == 1


class TestInvalid:

    def test_add_on_queue_full(self):
        receiver, subscriber = _recsub(max_size=1)

        receiver.add_data(data=123)

        with pytest.raises(BoboReceiverError):
            receiver.add_data(data=456)
