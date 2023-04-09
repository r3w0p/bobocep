# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Simple setup.
"""

from multiprocessing import cpu_count
from typing import List, Optional, Tuple

from bobocep.cep.action.handler import BoboActionHandler, BoboActionHandlerPool
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
from bobocep.cep.phenomenon import BoboPhenomenon
from bobocep.dist.crypto.aes import BoboDistributedCryptoAES
from bobocep.dist.device import BoboDevice
from bobocep.dist.tcp import BoboDistributedTCP
from bobocep.setup.setup import BoboSetup


class BoboSetupSimple(BoboSetup):
    """A simple setup to make configuration easier."""

    def __init__(
            self,
            phenomena: List[BoboPhenomenon],
            validator: Optional[BoboValidator] = None,
            handler: Optional[BoboActionHandler] = None,
            gen_event: Optional[BoboGenEvent] = None):
        """
        :param phenomena: A list of phenomena.
        :param validator: A data validator for the engine's Receiver task.
            Default: BoboValidatorAll.
        :param handler: An action handler.
            Default: BoboActionHandlerPool with processes equal to
            one less than the maximum system CPUs available.
        :param gen_event: An event generator.
            Default: None.
        """
        super().__init__()

        self._phenomena: List[BoboPhenomenon] = phenomena
        self._validator: BoboValidator = validator \
            if validator is not None else BoboValidatorAll()
        self._handler: BoboActionHandler = handler if handler is not None \
            else BoboActionHandlerPool(processes=max(1, cpu_count() - 1))
        self._gen_event: Optional[BoboGenEvent] = gen_event

    def generate(self) -> BoboEngine:
        """
        :return: The CEP engine.
        """
        receiver = BoboReceiver(
            validator=BoboValidatorAll(),
            gen_event_id=BoboGenEventIDUnique(),
            gen_timestamp=BoboGenTimestampEpoch(),
            gen_event=self._gen_event)

        decider = BoboDecider(
            phenomena=self._phenomena,
            gen_event_id=BoboGenEventIDUnique(),
            gen_run_id=BoboGenEventIDUnique())

        producer = BoboProducer(
            phenomena=self._phenomena,
            gen_event_id=BoboGenEventIDUnique(),
            gen_timestamp=BoboGenTimestampEpoch())

        forwarder = BoboForwarder(
            phenomena=self._phenomena,
            handler=self._handler,
            gen_event_id=BoboGenEventIDUnique())

        engine = BoboEngine(
            receiver=receiver,
            decider=decider,
            producer=producer,
            forwarder=forwarder)

        return engine


class BoboSetupDistributed(BoboSetup):
    """A setup to make distributed configuration easier."""

    def __init__(
            self,
            phenomena: List[BoboPhenomenon],
            urn: str,
            devices: List[BoboDevice],
            aes_key: str,
            validator: Optional[BoboValidatorJSONable] = None,
            handler: Optional[BoboActionHandler] = None,
            gen_event: Optional[BoboGenEvent] = None):
        """
        :param phenomena: A list of phenomena.
        :param urn: A URN that is unique across devices in the network.
        :param devices: Devices in the network (including this device).
        :param aes_key: The AES key to use for encryption.
        :param validator: A data validator for the engine's Receiver task.
            Default: BoboValidatorAll.
        :param handler: An action handler.
            Default: BoboActionHandlerPool with processes equal to
            one less than the maximum system CPUs available.
        :param gen_event: An event generator.
            Default: None.
        """
        super().__init__()

        self._setup_simple = BoboSetupSimple(
            phenomena=phenomena,
            validator=validator if validator is not None else
            BoboValidatorJSONable(),
            handler=handler,
            gen_event=gen_event
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

        return engine, distributed
