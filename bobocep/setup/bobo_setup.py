from threading import RLock
from time import time_ns
from typing import List
from uuid import uuid4

from pika import ConnectionParameters

from bobocep.decider.bobo_decider import BoboDecider
from bobocep.decider.buffers.shared_versioned_match_buffer import \
    SharedVersionedMatchBuffer
from bobocep.decider.decider_subscriber import IDeciderSubscriber
from bobocep.decider.handlers.bobo_nfa_handler import BoboNFAHandler
from bobocep.forwarder.action_forwarder import ActionForwarder
from bobocep.forwarder.forwarder_subscriber import IForwarderSubscriber
from bobocep.producer.action_producer import ActionProducer
from bobocep.producer.producer_subscriber import IProducerSubscriber
from bobocep.receiver.bobo_receiver import BoboReceiver
from bobocep.receiver.formatters.primitive_event_formatter import \
    PrimitiveEventFormatter
from bobocep.receiver.generators.bobo_null_data_generator import \
    BoboNullDataGenerator
from bobocep.receiver.generators.data.bobo_null_data import BoboNullData
from bobocep.receiver.receiver_subscriber import IReceiverSubscriber
from bobocep.receiver.validators.any_validator import AnyValidator
from bobocep.receiver.validators.bobo_validator import \
    BoboValidator
from bobocep.rules.actions.bobo_action import BoboAction
from bobocep.rules.actions.no_action import NoAction
from bobocep.rules.bobo_rule_builder import BoboRuleBuilder
from bobocep.setup.bobo_complex_event import \
    BoboComplexEvent
from bobocep.setup.distributed.bobo_dist_manager import BoboDistManager
from bobocep.setup.distributed.outgoing.dist_outgoing_subscriber import \
    IDistOutgoingSubscriber
from bobocep.setup.task.bobo_task_thread import BoboTaskThread


class BoboSetup(IDistOutgoingSubscriber):
    """A class to set up a working :code:`bobocep` process.

    :param delay: The delay, in seconds, for internal threads to wait before
                  repeating its processing task, defaults to 0.5.
    :type delay: float, optional

    :param recursive: Whether CompositeEvent instances should be put back
                      into the system on generation, defaults to True.
    :type recursive: bool, optional

    :param max_queue_size: The maximum data queue size,
                           defaults to 0 (infinite).
    :type max_queue_size: int, optional

    :param max_recent: The maximum number of recent CompositeEvent instances
                        generated by this handler to pass to runs.
                        Minimum of 1, defaults to 1.
    :type max_recent: int, optional
    """

    def __init__(self,
                 delay: float = 0.5,
                 recursive: bool = True,
                 max_queue_size: int = 0,
                 max_recent: int = 1) -> None:
        super().__init__()

        self._delay = delay
        self._recursive = recursive
        self._max_queue_size = max_queue_size
        self._max_recent = max(1, max_recent)

        self._lock = RLock()
        self._running = False
        self._cancelled = False
        self._configured = False

        self._validator = None
        self._event_defs = []
        self._action_producer = None
        self._action_forwarder = None

        self._req_null_data = False
        self._null_data_generator = None
        self._null_data_delay = 0
        self._null_data_obj = None

        self._distributed = False
        self._manager = None
        self._exchange_name = None
        self._user_name = None
        self._parameters = None
        self._user_id = None
        self._is_synced = False

        self._receiver = None
        self._decider = None
        self._producer = None
        self._forwarder = None

        self._receiver_thread = None
        self._null_event_thread = None
        self._decider_thread = None
        self._producer_thread = None
        self._forwarder_thread = None

        self._subs_receiver = []
        self._subs_decider = {}
        self._subs_producer = {}
        self._subs_forwarder = []

    def is_ready(self) -> bool:
        """
        :return: True if active and synced, False otherwise.
        """

        with self._lock:
            if self.is_active():
                if self._distributed:
                    return self._is_synced
                else:
                    return True

    def is_active(self) -> bool:
        """
        :return: True if running and not cancelled, False otherwise.
        """

        with self._lock:
            return self._running and not self._cancelled

    def is_inactive(self) -> bool:
        """
        :return: True if not running and not cancelled, False otherwise.
        """

        with self._lock:
            return not self._running and not self._cancelled

    def is_cancelled(self) -> bool:
        """
        :return: True if cancelled, False otherwise.
        """

        with self._lock:
            return self._cancelled

    def is_configured(self) -> bool:
        """
        :return: True if configured, False otherwise.
        """

        with self._lock:
            return self._configured

    def get_receiver(self) -> BoboReceiver:
        """
        :raises RuntimeError: Attempting access before configuration.

        :return: The Receiver.
        """

        with self._lock:
            if not self._configured:
                raise RuntimeError("Setup must be configured first.")

            return self._receiver

    def get_decider(self) -> BoboDecider:
        """
        :raises RuntimeError: Attempting access before configuration.

        :return: The Receiver.
        """

        with self._lock:
            if not self._configured:
                raise RuntimeError("Setup must be configured first.")

            return self._decider

    def get_producer(self) -> ActionProducer:
        """
        :raises RuntimeError: Attempting access before configuration.

        :return: The Receiver.
        """

        with self._lock:
            if not self._configured:
                raise RuntimeError("Setup must be configured first.")

            return self._producer

    def get_forwarder(self) -> ActionForwarder:
        """
        :raises RuntimeError: Attempting access before configuration.

        :return: The Forwarder.
        """

        with self._lock:
            if not self._configured:
                raise RuntimeError("Setup must be configured first.")

            return self._forwarder

    def get_distributed(self) -> BoboDistManager:
        """
        :raises RuntimeError: Attempting access before configuration.
        :raises RuntimeError: Distributed was not configured.

        :return: The distrubted manager.
        """

        with self._lock:
            if not self._configured:
                raise RuntimeError("Setup must be configured first.")
            elif not self._distributed:
                raise RuntimeError("Distributed was not configured.")

            return self._manager

    def get_null_data_generator(self) -> BoboNullDataGenerator:
        """
        :raises RuntimeError: Attempting access before configuration.

        :return: The null data generator, or None if one was not configured
         during setup.
        """

        with self._lock:
            if not self._configured:
                raise RuntimeError("Setup must be configured first.")

            return self._null_data_generator

    def get_complex_events(self) -> List[BoboComplexEvent]:
        """
        :return: A list of complex event definitions currently in setup.
        """

        with self._lock:
            if self.is_inactive():
                return self._event_defs[:]

    def add_complex_event(self, event_def: BoboComplexEvent) -> None:
        """
        Adds a complex event definition to the setup.

        :param event_def: The complex event definition.
        :type event_def: BoboComplexEvent
        """

        with self._lock:
            if self.is_inactive():
                self._event_defs.append(event_def)

    def config_receiver(self, validator: BoboValidator) -> None:
        """
        Configure the Receiver.

        :param validator: The validator to use in the Receiver.
        :type validator: BoboValidator
        """

        with self._lock:
            if self.is_inactive():
                self._validator = validator

    def config_producer(self, action: BoboAction) -> None:
        """
        Configure the Producer.

        :param action: The action to execute in the Producer on CompositeEvent
                       generation. If this action returns True, the
                       CompositeEvent is passed to the Forwarder. Otherwise,
                       it is dropped.
        :type action: BoboAction
        """

        with self._lock:
            if self.is_inactive():
                self._action_producer = action

    def config_forwarder(self, action: BoboAction) -> None:
        """
        Configure the Forwarder.

        :param action: The action to execute in the Forwarder. If this action
                       returns True, the CompositeEvent is passed to the
                       Forwarder's subscribers. Otherwise, it is dropped.
        :type action: BoboAction
        """

        with self._lock:
            if self.is_inactive():
                self._action_forwarder = action

    def config_distributed(self,
                           exchange_name: str,
                           user_name: str,
                           parameters: ConnectionParameters) -> None:
        """
        Configure the connection to the external message broker.

        :param exchange_name: The exchange name.
        :type exchange_name: str

        :param user_name: The user name.
        :type user_name: str

        :param parameters: Parameters to connect to a message broker.
        :type parameters: ConnectionParameters
        """

        with self._lock:
            if self.is_inactive():
                self._distributed = True
                self._exchange_name = exchange_name
                self._user_name = user_name
                self._parameters = parameters

    def config_null_data(self,
                         delay_sec: float,
                         null_data: BoboNullData) -> None:
        """
        Configure static data to be input periodically into the Receiver.

        :param delay_sec: The rate at which to send data. Minimum of 0.1
                          seconds.
        :type delay_sec: float

        :param null_data: The data to send. Ensure that it is able to pass the
                          Receiver's validation criteria. Otherwise, the null
                          data will not enter the system.
        :type null_data: BoboNullData
        """

        with self._lock:
            if self.is_inactive():
                self._req_null_data = True
                self._null_data_delay = max(0.1, delay_sec)
                self._null_data_obj = null_data

    def on_sync(self) -> None:
        with self._lock:
            if self._distributed:
                self._activate_tasks()
            self._is_synced = True

    def start(self) -> None:
        """Start the setup.

        :raises RuntimeError: Running setup when it is already active.
        :raises RuntimeError: No complex event definitions found.
        """

        with self._lock:
            if self.is_active():
                raise RuntimeError("Setup is already active.")

            if not self._configured:
                self.configure()
            self._start_threads()
            self._running = True

            # tasks active by default if not distributed, sync immediately
            if not self._distributed:
                self._is_synced = True

    def configure(self) -> None:
        with self._lock:
            if self._cancelled:
                raise RuntimeError("Setup has been cancelled.")

            if self.is_active():
                raise RuntimeError("Setup is already active.")

            if self._configured:
                raise RuntimeError("Setup is already configured.")

            if len(self._event_defs) == 0:
                raise RuntimeError(
                    "No complex event definitions found. "
                    "At least one must be provided.")

            self._config_receiver()
            self._config_decider()
            self._config_producer()
            self._config_forwarder()

            self._config_distributed()
            self._config_definitions()
            self._config_extra_subscriptions()

            self._configured = True

    def cancel(self) -> None:
        """Cancel the setup."""

        with self._lock:
            if not self._cancelled:
                self._cancelled = True
                if self._running:
                    self._running = False
                    self._deactivate_tasks()
                    self._stop_threads()

    def subscribe_receiver(self, subscriber: IReceiverSubscriber) -> None:
        with self._lock:
            if self.is_inactive():
                if subscriber not in self._subs_receiver:
                    self._subs_receiver.append(subscriber)

    def subscribe_decider(self,
                          nfa_name: str,
                          subscriber: IDeciderSubscriber) -> None:
        with self._lock:
            if self.is_inactive():
                if nfa_name not in self._subs_decider:
                    self._subs_decider[nfa_name] = []

                if subscriber not in self._subs_decider[nfa_name]:
                    self._subs_decider[nfa_name].append(subscriber)

    def subscribe_producer(self,
                           nfa_name: str,
                           subscriber: IProducerSubscriber) -> None:
        with self._lock:
            if self.is_inactive():
                if nfa_name not in self._subs_producer:
                    self._subs_producer[nfa_name] = []

                if subscriber not in self._subs_producer[nfa_name]:
                    self._subs_producer[nfa_name].append(subscriber)

    def subscribe_forwarder(self, subscriber: IForwarderSubscriber) -> None:
        with self._lock:
            if self.is_inactive() and subscriber not in self._subs_forwarder:
                self._subs_forwarder.append(subscriber)

    def _config_receiver(self) -> None:
        if self._validator is None:
            self._validator = AnyValidator()

        self._receiver = BoboReceiver(
            validator=self._validator,
            formatter=PrimitiveEventFormatter(),
            max_queue_size=self._max_queue_size,
            active=(not self._distributed))

        self._receiver_thread = BoboTaskThread(
            task=self._receiver,
            delay=self._delay)

        if self._req_null_data:
            self._null_data_generator = BoboNullDataGenerator(
                receiver=self._receiver,
                null_data=self._null_data_obj,
                active=(not self._distributed))

            self._null_event_thread = BoboTaskThread(
                task=self._null_data_generator,
                delay=self._null_data_delay
            )

    def _config_decider(self) -> None:
        self._decider = BoboDecider(
            recursive=self._recursive,
            max_queue_size=self._max_queue_size,
            active=(not self._distributed))

        self._decider_thread = BoboTaskThread(
            task=self._decider,
            delay=self._delay)

        # Receiver -> Decider
        self._receiver.subscribe(self._decider)

    def _config_producer(self) -> None:
        if self._action_producer is None:
            self._action_producer = NoAction()

        self._producer = ActionProducer(
            action=self._action_producer,
            max_queue_size=self._max_queue_size,
            active=(not self._distributed))

        self._producer_thread = BoboTaskThread(
            task=self._producer,
            delay=self._delay)

    def _config_forwarder(self) -> None:
        if self._action_forwarder is None:
            self._action_forwarder = NoAction()

        self._forwarder = ActionForwarder(
            action=self._action_forwarder,
            max_queue_size=self._max_queue_size,
            active=(not self._distributed))

        self._forwarder_thread = BoboTaskThread(
            task=self._forwarder,
            delay=self._delay)

    def _config_distributed(self) -> None:
        if self._distributed:
            self._user_id = "{}-{}-{}".format(
                self._user_name,
                uuid4(),
                time_ns())

            self._manager = BoboDistManager(
                decider=self._decider,
                exchange_name=self._exchange_name,
                user_id=self._user_id,
                parameters=self._parameters,
                delay=self._delay)

            # setup will activate tasks on sync
            self._manager.outgoing.subscribe(self)

    def _config_definitions(self) -> None:
        for event_def in self._event_defs:
            handler = BoboNFAHandler(
                nfa=BoboRuleBuilder.nfa(
                    name_nfa=event_def.name,
                    pattern=event_def.pattern),
                buffer=SharedVersionedMatchBuffer(),
                max_recent=self._max_recent)

            self._decider.add_nfa_handler(handler)

            # Decider -> Producer
            self._decider.subscribe(event_def.name, self._producer)

            if self._recursive:
                # Producer -> Decider
                self._producer.subscribe(event_def.name, self._decider)

            # Producer -> Forwarder
            self._producer.subscribe(event_def.name, self._forwarder)

            if event_def.action is not None:
                # Producer -> Action
                self._producer.subscribe(event_def.name, event_def.action)

                # Action -> Producer
                event_def.action.subscribe(self._producer)

            if self._distributed:
                # Handler -> Outgoing
                handler.subscribe(self._manager.outgoing)

                # Producer -> Outgoing
                self._producer.subscribe(event_def.name,
                                         self._manager.outgoing)

    def _config_extra_subscriptions(self):
        # receiver
        for sub in self._subs_receiver:
            self._receiver.subscribe(sub)

        # decider
        for nfa_name, subs in self._subs_decider.items():
            for sub in subs:
                self._decider.subscribe(nfa_name, sub)

        # producer
        for nfa_name, subs in self._subs_producer.items():
            for sub in subs:
                self._producer.subscribe(nfa_name, sub)

        # forwarder
        for sub in self._subs_forwarder:
            self._forwarder.subscribe(sub)

    def _start_threads(self) -> None:
        self._receiver_thread.start()
        self._decider_thread.start()
        self._producer_thread.start()
        self._forwarder_thread.start()

        if self._null_event_thread is not None:
            self._null_event_thread.start()

        if self._manager is not None:
            self._manager.start()

    def _stop_threads(self) -> None:
        self._receiver_thread.cancel()
        self._decider_thread.cancel()
        self._producer_thread.cancel()
        self._forwarder_thread.cancel()

        if self._null_event_thread is not None:
            self._null_event_thread.cancel()

        if self._manager is not None:
            self._manager.cancel()

    def _activate_tasks(self) -> None:
        self._forwarder.activate()
        self._producer.activate()
        self._decider.activate()
        self._receiver.activate()

        if self._null_data_generator is not None:
            self._null_data_generator.activate()

    def _deactivate_tasks(self) -> None:
        if self._null_data_generator is not None:
            self._null_data_generator.deactivate()

        self._receiver.deactivate()
        self._decider.deactivate()
        self._producer.deactivate()
        self._forwarder.deactivate()