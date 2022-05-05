# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from bobocep.event.event_id.bobo_event_id_standard import BoboEventIDStandard


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
