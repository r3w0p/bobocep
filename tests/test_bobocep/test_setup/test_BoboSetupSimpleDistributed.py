# Copyright (c) 2019-2024 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from bobocep.cep.action import BoboActionHandlerBlocking
from bobocep.cep.phenom import BoboPattern, BoboPatternBuilder, BoboPhenomenon
from bobocep.dist.device import BoboDevice
from bobocep.setup.simple import BoboSetupSimpleDistributed


class TestValid:

    def test_phenomena(self):
        pattern: BoboPattern = BoboPatternBuilder("pattern") \
            .followed_by(lambda e, h: str(e.data) == "a") \
            .followed_by(lambda e, h: str(e.data) == "b") \
            .followed_by(lambda e, h: str(e.data) == "c") \
            .haltcondition(lambda e, h: str(e.data) == "h") \
            .generate()

        phenomenon = BoboPhenomenon(
            name="phenomenon",
            patterns=[pattern],
            action=None
        )

        devices = [
            BoboDevice(
                addr="127.0.0.1",
                port=8081,
                urn="urn:bobocep:device:1",
                id_key="id_key_device_1"
            ),
            BoboDevice(
                addr="127.0.0.1",
                port=8082,
                urn="urn:bobocep:device:2",
                id_key="id_key_device_2"
            )
        ]

        setup = BoboSetupSimpleDistributed(
            phenomena=[phenomenon],
            handler=BoboActionHandlerBlocking(),
            urn="urn:bobocep:device:1",
            devices=devices,
            aes_key="1234567890ABCDEF"
        )

        engine, dist = setup.generate()
        dec_phenomena = engine.decider.phenomena()
        assert len(dec_phenomena) == 1

        dec_phenomena_names = [dp.name for dp in dec_phenomena]
        assert phenomenon.name in dec_phenomena_names
