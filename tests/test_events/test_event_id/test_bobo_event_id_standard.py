# Copyright (c) The BoboCEP Authors
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License v3.0.

from bobocep.events.event_id.bobo_event_id_standard import BoboEventIDStandard


def test_output_type_length():
    generator = BoboEventIDStandard()
    event_id = generator.generate()

    assert type(event_id) == str
    assert len(event_id) > 0


def test_1_generator_2_different_outputs():
    generator = BoboEventIDStandard()

    event_id_1 = generator.generate()
    event_id_2 = generator.generate()

    assert event_id_1 != event_id_2
