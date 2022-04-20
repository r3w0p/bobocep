# Copyright (c) The BoboCEP Authors
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License v3.0.

import pytest

from bobocep.engine.receiver.bobo_receiver import BoboReceiver
from bobocep.engine.receiver.bobo_receiver_subscriber import \
    BoboReceiverSubscriber
from bobocep.engine.receiver.validator.bobo_validator_all import \
    BoboValidatorAll
from bobocep.events.bobo_event import BoboEvent
from bobocep.events.bobo_event_primitive import BoboEventPrimitive
from bobocep.events.event_id.bobo_event_id_standard import \
    BoboEventIDStandard
from bobocep.exceptions.engine.bobo_receiver_queue_full_error import \
    BoboReceiverQueueFullError


class TestReceiverSubscriber(BoboReceiverSubscriber):
    def __init__(self):
        super().__init__()
        self.events = []

    def on_receiver_event(self, event: BoboEvent):
        self.events.append(event)


def test_size_add_1_event_then_update():
    receiver = BoboReceiver(
        validator=BoboValidatorAll(),
        event_id_gen=BoboEventIDStandard(),
        null_event_gen=None,
        max_size=255)

    assert receiver.size() == 0
    receiver.add_data(data=123)
    assert receiver.size() == 1
    receiver.update()
    assert receiver.size() == 0


def test_subscriber_add_1_event_then_update():
    receiver = BoboReceiver(
        validator=BoboValidatorAll(),
        event_id_gen=BoboEventIDStandard(),
        null_event_gen=None,
        max_size=255)

    subscriber = TestReceiverSubscriber()
    receiver.subscribe(subscriber=subscriber)

    data = 123
    receiver.add_data(data=data)
    receiver.update()

    assert len(subscriber.events) == 1
    assert isinstance(subscriber.events[0], BoboEventPrimitive)
    assert subscriber.events[0].data == data


def test_add_on_queue_full():
    receiver = BoboReceiver(
        validator=BoboValidatorAll(),
        event_id_gen=BoboEventIDStandard(),
        null_event_gen=None,
        max_size=1)

    receiver.add_data(data=123)

    with pytest.raises(BoboReceiverQueueFullError):
        receiver.add_data(data=456)


def test_update_on_queue_empty():
    receiver = BoboReceiver(
        validator=BoboValidatorAll(),
        event_id_gen=BoboEventIDStandard(),
        null_event_gen=None,
        max_size=255)

    assert receiver.update() is None
