# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from bobocep.event.event_id.bobo_event_id_unique import BoboEventIDUnique


def test_output_type_length():
    generator = BoboEventIDUnique()
    event_id = generator.generate()

    assert len(event_id) > 0


def test_1_generator_2_different_outputs():
    generator = BoboEventIDUnique()

    event_id_1 = generator.generate()
    event_id_2 = generator.generate()

    assert event_id_1 != event_id_2
