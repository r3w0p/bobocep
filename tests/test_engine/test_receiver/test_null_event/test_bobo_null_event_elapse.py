# Copyright (c) 2022 The BoboCEP Authors
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from time import sleep

from bobocep.engine.receiver.null_event.bobo_null_event_elapse import \
    BoboNullEventElapse
from bobocep.events.bobo_event_primitive import BoboEventPrimitive


def test_not_from_now():
    gen = BoboNullEventElapse(1000, lambda: 123, from_now=False)
    event_id = "id"
    event = gen.maybe_generate(event_id)

    assert type(event) == BoboEventPrimitive
    assert event.event_id == event_id
    assert event.data == 123


def test_from_now_not_gen():
    gen = BoboNullEventElapse(int(3.6e+6), lambda: 123)
    event = gen.maybe_generate("id")

    assert event is None


def test_from_now_gen():
    gen = BoboNullEventElapse(1, lambda: 123)
    sleep(1)
    event = gen.maybe_generate("id")

    assert type(event) == BoboEventPrimitive
