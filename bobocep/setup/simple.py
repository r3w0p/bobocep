# Copyright (c) 2019-2024 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Simple setup.
"""

from typing import List, Optional, Tuple

from bobocep.cep.action.handler import BoboActionHandler
from bobocep.cep.engine.decider.decider import BoboDecider
from bobocep.cep.engine.engine import BoboEngine
from bobocep.cep.engine.forwarder.forwarder import BoboForwarder
from bobocep.cep.engine.producer.producer import BoboProducer
from bobocep.cep.engine.receiver.receiver import BoboReceiver
from bobocep.cep.engine.receiver.validator import BoboValidator, \
    BoboValidatorAll, BoboValidatorJSONable
from bobocep.cep.gen.event import BoboGenEvent
from bobocep.cep.gen.event_id import BoboGenEventIDUnique
from bobocep.cep.gen.timestamp import BoboGenTimestampEpoch
from bobocep.cep.phenom.phenom import BoboPhenomenon
from bobocep.dist.crypto.aes import BoboDistributedCryptoAES
from bobocep.dist.device import BoboDevice
from bobocep.dist.tcp import BoboDistributedTCP
from bobocep.setup.setup import BoboSetup


class BoboSetupSimple(BoboSetup):
    """A simple setup to make configuration easier."""

    def __init__(
            self,
            phenomena: List[BoboPhenomenon],
            handler: BoboActionHandler,
            validator: Optional[BoboValidator] = None,
            gen_event: Optional[BoboGenEvent] = None,
            urn: Optional[str] = None
    ):
        """
        :param phenomena: A list of phenomena.
        :param handler: An action handler.
        :param validator: A data validator for the engine's Receiver task.
            Default: BoboValidatorAll.
        :param gen_event: An event generator.
            Default: None.
        :param urn: A URN for ID generation.
        """
        super().__init__()

        self._phenomena: List[BoboPhenomenon] = phenomena
        self._validator: BoboValidator = validator \
            if validator is not None else BoboValidatorAll()
        self._handler: BoboActionHandler = handler
        self._gen_event: Optional[BoboGenEvent] = gen_event
        self._urn: Optional[str] = urn

    def generate(self) -> BoboEngine:
        """
        :return: The CEP engine.
        """
        gen_event_id = BoboGenEventIDUnique(self._urn)
        gen_run_id = BoboGenEventIDUnique(self._urn)
        gen_timestamp = BoboGenTimestampEpoch()

        receiver = BoboReceiver(
            validator=self._validator,
            gen_event_id=gen_event_id,
            gen_timestamp=gen_timestamp,
            gen_event=self._gen_event)

        decider = BoboDecider(
            phenomena=self._phenomena,
            gen_event_id=gen_event_id,
            gen_run_id=gen_run_id)

        producer = BoboProducer(
            phenomena=self._phenomena,
            gen_event_id=gen_event_id,
            gen_timestamp=gen_timestamp)

        forwarder = BoboForwarder(
            phenomena=self._phenomena,
            handler=self._handler,
            gen_event_id=gen_event_id,
            gen_timestamp=gen_timestamp)

        engine = BoboEngine(
            receiver=receiver,
            decider=decider,
            producer=producer,
            forwarder=forwarder)

        return engine


class BoboSetupSimpleDistributed(BoboSetup):
    """
    A simple setup to make distributed configuration easier.
    """

    def __init__(
            self,
            phenomena: List[BoboPhenomenon],
            handler: BoboActionHandler,
            urn: str,
            devices: List[BoboDevice],
            aes_key: str,
            validator: Optional[BoboValidatorJSONable] = None,
            gen_event: Optional[BoboGenEvent] = None):
        """
        :param phenomena: A list of phenomena.
        :param handler: An action handler.
        :param urn: A URN that is unique across devices in the network.
        :param devices: Devices in the network (including this device).
        :param aes_key: The AES key to use for encryption.
        :param validator: A data validator for the engine's Receiver task.
            Default: BoboValidatorAll.
        :param gen_event: An event generator.
            Default: None.
        """
        super().__init__()

        self._setup_simple = BoboSetupSimple(
            phenomena=phenomena,
            handler=handler,
            validator=validator if validator is not None else
            BoboValidatorJSONable(),
            gen_event=gen_event,
            urn=urn
        )

        self._urn: str = urn
        self._devices: List[BoboDevice] = devices
        self._aes_key: str = aes_key

    def generate(self) -> Tuple[BoboEngine, BoboDistributedTCP]:
        """
        :return: The CEP engine and distributed TCP instance
            with AES encryption.
        """
        engine: BoboEngine = self._setup_simple.generate()

        distributed: BoboDistributedTCP = BoboDistributedTCP(
            urn=self._urn,
            decider=engine.decider,
            devices=self._devices,
            crypto=BoboDistributedCryptoAES(aes_key=self._aes_key))

        engine.decider.subscribe(distributed)
        distributed.subscribe(engine.decider)

        return engine, distributed
