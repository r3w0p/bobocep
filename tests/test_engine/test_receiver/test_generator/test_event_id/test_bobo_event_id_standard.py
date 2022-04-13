from bobocep.engine.receiver.generator.event_id.bobo_event_id_standard import BoboEventIDStandard


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
