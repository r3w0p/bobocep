# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from bobocep.cep.event import BoboEventSimple
from bobocep.cep.gen.event import BoboGenEventTime


class TestValid:

    def test_not_from_now(self):
        gen = BoboGenEventTime(1000, lambda: 123, from_now=False)
        event_id = "id"
        event = gen.maybe_generate(event_id)

        assert type(event) == BoboEventSimple
        assert event.event_id == event_id
        assert event.data == 123

    def test_from_now_not_gen(self):
        gen = BoboGenEventTime(int(3.6e+6), lambda: 123, from_now=True)
        event = gen.maybe_generate("id")

        assert event is None
