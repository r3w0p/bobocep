# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from bobocep.cep.gen.event_id import BoboGenEventIDUnique


class TestValid:

    def test_output_length_greater_than_zero(self):
        generator = BoboGenEventIDUnique()
        event_id = generator.generate()

        assert len(event_id) > 0

    def test_1_generator_2_unique_outputs(self):
        generator = BoboGenEventIDUnique()

        event_id_1 = generator.generate()
        event_id_2 = generator.generate()

        assert event_id_1 != event_id_2

    def test_urn(self):
        urn = "test_urn"
        generator = BoboGenEventIDUnique(urn=urn)

        event_id_1 = generator.generate()

        assert event_id_1.startswith(urn)
