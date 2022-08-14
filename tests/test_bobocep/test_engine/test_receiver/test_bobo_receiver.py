# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

import tests.common as tc
from bobocep.engine.receiver.bobo_receiver_error import BoboReceiverError
from bobocep.engine.receiver.event_gen.bobo_event_gen_time import \
    BoboEventGenTime
from bobocep.engine.receiver.validator.bobo_validator_not_type import \
    BoboValidatorNotType
from bobocep.event.bobo_event_simple import BoboEventSimple


class TestValid:

    def test_size_add_1_event_then_update(self):
        receiver, subscriber = tc.receiver_sub()

        assert receiver.size() == 0
        receiver.add_data(data=123)
        assert receiver.size() == 1
        receiver.update()
        assert receiver.size() == 0

    def test_subscriber_add_1_event_then_update(self):
        receiver, subscriber = tc.receiver_sub()

        data = 123
        receiver.add_data(data=data)
        receiver.update()

        assert len(subscriber.output) == 1
        assert isinstance(subscriber.output[0], BoboEventSimple)
        assert subscriber.output[0].data == data

    def test_update_on_queue_empty(self):
        receiver, subscriber = tc.receiver_sub()

        assert receiver.update() is False

    def test_validator_invalid_data(self):
        receiver, subscriber = tc.receiver_sub(
            validator=BoboValidatorNotType(types=[type(None)]))

        data = None
        receiver.add_data(data=data)
        receiver.update()

        assert len(subscriber.output) == 0

    def test_null_event(self):
        data_null_event = 456

        receiver, subscriber = tc.receiver_sub(
            event_gen=BoboEventGenTime(
                milliseconds=1,
                datagen=lambda: data_null_event,
                from_now=False))

        data = 123
        receiver.add_data(data=data)
        receiver.update()

        assert len(subscriber.output) == 2
        assert isinstance(subscriber.output[0], BoboEventSimple)
        assert isinstance(subscriber.output[1], BoboEventSimple)
        assert subscriber.output[0].data == data
        assert subscriber.output[1].data == data_null_event

    def test_process_add_data_event_simple(self):
        receiver, subscriber = tc.receiver_sub()
        assert receiver.size() == 0

        event = tc.event_simple()
        receiver.add_data(data=event)
        receiver.update()

        assert len(subscriber.output) == 1
        assert subscriber.output[0] == event

    def test_on_producer_complex_event(self):
        receiver, subscriber = tc.receiver_sub()
        assert receiver.size() == 0

        receiver.on_producer_complex_event(event=tc.event_complex())
        assert receiver.size() == 1

    def test_on_forwarder_action_event(self):
        receiver, subscriber = tc.receiver_sub()

        assert receiver.size() == 0

        receiver.on_forwarder_action_event(event=tc.event_action())
        assert receiver.size() == 1


class TestInvalid:

    def test_add_on_queue_full(self):
        receiver, subscriber = tc.receiver_sub(max_size=1)

        receiver.add_data(data=123)

        with pytest.raises(BoboReceiverError):
            receiver.add_data(data=456)
