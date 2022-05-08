# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

from bobocep.engine.receiver.bobo_receiver import BoboReceiver
from bobocep.engine.receiver.bobo_receiver_subscriber import \
    BoboReceiverSubscriber
from bobocep.engine.receiver.exception.bobo_receiver_queue_full_error import \
    BoboReceiverQueueFullError
from bobocep.engine.receiver.validator.bobo_validator_all import \
    BoboValidatorAll
from bobocep.event.bobo_event import BoboEvent
from bobocep.event.bobo_event_simple import BoboEventSimple
from bobocep.event.event_id.bobo_event_id_unique import \
    BoboEventIDUnique


class StubReceiverSubscriber(BoboReceiverSubscriber):
    def __init__(self):
        super().__init__()
        self.events = []

    def on_receiver_event(self, event: BoboEvent):
        self.events.append(event)


def test_size_add_1_event_then_update():
    receiver = BoboReceiver(
        validator=BoboValidatorAll(),
        event_id_gen=BoboEventIDUnique(),
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
        event_id_gen=BoboEventIDUnique(),
        null_event_gen=None,
        max_size=255)

    subscriber = StubReceiverSubscriber()
    receiver.subscribe(subscriber=subscriber)

    data = 123
    receiver.add_data(data=data)
    receiver.update()

    assert len(subscriber.events) == 1
    assert isinstance(subscriber.events[0], BoboEventSimple)
    assert subscriber.events[0].data == data


def test_add_on_queue_full():
    receiver = BoboReceiver(
        validator=BoboValidatorAll(),
        event_id_gen=BoboEventIDUnique(),
        null_event_gen=None,
        max_size=1)

    receiver.add_data(data=123)

    with pytest.raises(BoboReceiverQueueFullError):
        receiver.add_data(data=456)


def test_update_on_queue_empty():
    receiver = BoboReceiver(
        validator=BoboValidatorAll(),
        event_id_gen=BoboEventIDUnique(),
        null_event_gen=None,
        max_size=255)

    assert receiver.update() is None
