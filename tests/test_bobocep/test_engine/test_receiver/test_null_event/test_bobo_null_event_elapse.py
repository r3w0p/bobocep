# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from time import sleep

from bobocep.engine.receiver.time_event.bobo_time_event_elapse import \
    BoboTimeEventElapse
from bobocep.event.bobo_event_simple import BoboEventSimple


def test_not_from_now():
    gen = BoboTimeEventElapse(1000, lambda: 123, from_now=False)
    event_id = "id"
    event = gen.maybe_generate(event_id)

    assert type(event) == BoboEventSimple
    assert event.event_id == event_id
    assert event.data == 123


def test_from_now_not_gen():
    gen = BoboTimeEventElapse(int(3.6e+6), lambda: 123)
    event = gen.maybe_generate("id")

    assert event is None


def test_from_now_gen():
    gen = BoboTimeEventElapse(1, lambda: 123)
    sleep(1)
    event = gen.maybe_generate("id")

    assert type(event) == BoboEventSimple
