import unittest
from time import sleep

from bobocep.decider.decider_subscriber import IDeciderSubscriber
from bobocep.forwarder.forwarder_subscriber import IForwarderSubscriber
from bobocep.producer.producer_subscriber import IProducerSubscriber
from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.receiver.generators.data.bobo_null_data_static import \
    BoboNullDataStatic
from bobocep.receiver.receiver_subscriber import IReceiverSubscriber
from bobocep.receiver.validators.str_dict_validator import StrDictValidator
from bobocep.rules.actions.no_action import NoAction
from bobocep.rules.actions.rate_limit_action import RateLimitAction
from bobocep.rules.events.action_event import ActionEvent
from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.rules.nfas.patterns.bobo_pattern import BoboPattern
from bobocep.rules.predicates.bobo_predicate_callable import \
    BoboPredicateCallable
from bobocep.setup.bobo_complex_event import BoboComplexEvent
from bobocep.setup.bobo_setup import BoboSetup

from pika import ConnectionParameters, PlainCredentials

EXCHANGE_NAME = "test_exchange_name"
USER_NAME = "test_user_name"

NAME_NFA_A = "name_nfa_a"
NAME_NFA_B = "name_nfa_b"
NAME_NFA_C = "name_nfa_c"
RUN_ID_A = "run_id_a"

LABEL_A = "label_a"
LABEL_B = "label_b"
LABEL_C = "label_c"
LABEL_D = "label_d"

KEY_A = "key_a"
VALUE_A = "value_a"
DATA_DICT_A = {KEY_A: VALUE_A}

SLEEP_WAIT = 0.5
NULL_DATA_DELAY = 1

stub_predicate_true = BoboPredicateCallable(lambda e, h, r: True)

stub_pattern_1 = BoboPattern().followed_by(
    label=LABEL_A,
    predicate=stub_predicate_true
)

stub_pattern_4 = BoboPattern() \
    .followed_by(
    label=LABEL_A,
    predicate=stub_predicate_true
).followed_by(
    label=LABEL_B,
    predicate=stub_predicate_true
).followed_by(
    label=LABEL_C,
    predicate=stub_predicate_true
).followed_by(
    label=LABEL_D,
    predicate=stub_predicate_true
)

event_a = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())
event_b = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())
event_c = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())
event_d = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())

credentials = PlainCredentials('guest', 'guest')
parameters = ConnectionParameters("127.0.0.1", 5672, '/', credentials)


class StubSubscriberSetup(IReceiverSubscriber,
                          IDeciderSubscriber,
                          IProducerSubscriber,
                          IForwarderSubscriber):

    def __init__(self) -> None:
        super().__init__()

        self.receiver_event = []
        self.invalid_data = []
        self.decider_complex_event = []
        self.accepted_producer_event = []
        self.rejected_producer_event = []
        self.producer_action = []
        self.forwarder_success_event = []
        self.forwarder_failure_event = []

    def on_receiver_event(self, event: PrimitiveEvent):
        self.receiver_event.append(event)

    def on_invalid_data(self, data):
        self.invalid_data.append(data)

    def on_decider_complex_event(self, event: CompositeEvent):
        self.decider_complex_event.append(event)

    def on_accepted_producer_event(self, event: CompositeEvent):
        self.accepted_producer_event.append(event)

    def on_rejected_producer_event(self, event: CompositeEvent):
        self.rejected_producer_event.append(event)

    def on_producer_action(self, event: ActionEvent):
        self.producer_action.append(event)

    def on_forwarder_success_event(self, event: BoboEvent):
        self.forwarder_success_event.append(event)

    def on_forwarder_failure_event(self, event: BoboEvent):
        self.forwarder_failure_event.append(event)


class TestBoboSetup(unittest.TestCase):

    def test_setup_before_configure(self):
        setup = BoboSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_1,
                action=NoAction()
            ))

        setup.config_null_data(
            delay_sec=NULL_DATA_DELAY,
            null_data=BoboNullDataStatic(DATA_DICT_A))

        self.assertFalse(setup.is_ready())
        self.assertFalse(setup.is_active())
        self.assertTrue(setup.is_inactive())
        self.assertFalse(setup.is_cancelled())
        self.assertFalse(setup.is_configured())

    def test_setup_after_configure(self):
        setup = BoboSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_1,
                action=NoAction()
            ))

        setup.config_null_data(
            delay_sec=NULL_DATA_DELAY,
            null_data=BoboNullDataStatic(DATA_DICT_A))

        setup.configure()

        self.assertFalse(setup.is_ready())
        self.assertFalse(setup.is_active())
        self.assertTrue(setup.is_inactive())
        self.assertFalse(setup.is_cancelled())
        self.assertTrue(setup.is_configured())

        self.assertTrue(setup.get_receiver().is_active())
        self.assertTrue(setup.get_decider().is_active())
        self.assertTrue(setup.get_producer().is_active())
        self.assertTrue(setup.get_forwarder().is_active())
        self.assertTrue(setup.get_null_data_generator().is_active())

    def test_setup_after_start(self):
        setup = BoboSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_1,
                action=NoAction()
            ))

        setup.config_null_data(
            delay_sec=NULL_DATA_DELAY,
            null_data=BoboNullDataStatic(DATA_DICT_A))

        setup.configure()
        setup.start()

        self.assertTrue(setup.is_ready())
        self.assertTrue(setup.is_active())
        self.assertFalse(setup.is_inactive())
        self.assertFalse(setup.is_cancelled())
        self.assertTrue(setup.is_configured())

        self.assertTrue(setup.get_receiver().is_active())
        self.assertTrue(setup.get_decider().is_active())
        self.assertTrue(setup.get_producer().is_active())
        self.assertTrue(setup.get_forwarder().is_active())
        self.assertTrue(setup.get_null_data_generator().is_active())

        setup.cancel()

    def test_setup_after_cancel(self):
        setup = BoboSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_1,
                action=NoAction()
            ))

        setup.config_null_data(
            delay_sec=NULL_DATA_DELAY,
            null_data=BoboNullDataStatic(DATA_DICT_A))

        setup.configure()
        setup.start()
        sleep(SLEEP_WAIT)
        setup.cancel()

        self.assertFalse(setup.is_ready())
        self.assertFalse(setup.is_active())
        self.assertFalse(setup.is_inactive())
        self.assertTrue(setup.is_cancelled())
        self.assertTrue(setup.is_configured())

        self.assertFalse(setup.get_receiver().is_active())
        self.assertFalse(setup.get_decider().is_active())
        self.assertFalse(setup.get_producer().is_active())
        self.assertFalse(setup.get_forwarder().is_active())
        self.assertFalse(setup.get_null_data_generator().is_active())

    def test_config_arguments(self):
        setup = BoboSetup()

        event_def = BoboComplexEvent(
            NAME_NFA_A,
            stub_pattern_1)
        validator = StrDictValidator()
        action_producer = RateLimitAction()
        action_forwarder = NoAction()
        null_data = BoboNullDataStatic(DATA_DICT_A)

        setup.add_complex_event(event_def)
        setup.config_receiver(validator)
        setup.config_producer(action_producer)
        setup.config_forwarder(action_forwarder)
        setup.config_null_data(NULL_DATA_DELAY, null_data)
        setup.config_distributed(EXCHANGE_NAME,
                                 USER_NAME,
                                 parameters)
        setup.configure()

        receiver = setup.get_receiver()
        decider = setup.get_decider()
        producer = setup.get_producer()
        forwarder = setup.get_forwarder()
        nullgen = setup.get_null_data_generator()
        manager = setup.get_distributed()

        self.assertEqual(validator, receiver.get_validator())
        self.assertEqual(NAME_NFA_A, decider.get_all_handlers()[0].nfa.name)
        self.assertEqual(action_producer, producer._action)
        self.assertEqual(action_forwarder, forwarder._action)

        self.assertEqual(null_data, nullgen.null_data)
        self.assertEqual(receiver, nullgen.receiver)

        self.assertEqual(manager.outgoing.decider, decider)
        self.assertEqual(manager.outgoing.exchange_name, EXCHANGE_NAME)
        self.assertTrue(manager.outgoing.user_id.find(USER_NAME) != -1)
        self.assertEqual(manager.outgoing.parameters, parameters)

        self.assertEqual(manager.incoming.decider, decider)
        self.assertEqual(manager.incoming.exchange_name, EXCHANGE_NAME)
        self.assertTrue(manager.incoming.user_id.find(USER_NAME) != -1)
        self.assertEqual(manager.incoming.parameters, parameters)

    def test_access_before_configuration(self):
        setup = BoboSetup()

        with self.assertRaises(RuntimeError):
            setup.get_receiver()

        with self.assertRaises(RuntimeError):
            setup.get_decider()

        with self.assertRaises(RuntimeError):
            setup.get_producer()

        with self.assertRaises(RuntimeError):
            setup.get_forwarder()

        with self.assertRaises(RuntimeError):
            setup.get_distributed()

        with self.assertRaises(RuntimeError):
            setup.get_null_data_generator()

    def test_configure_when_cancelled(self):
        setup = BoboSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_1,
                action=NoAction()
            ))
        setup.cancel()

        with self.assertRaises(RuntimeError):
            setup.configure()

        self.assertFalse(setup.is_configured())

    def test_configure_when_active(self):
        setup = BoboSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_1,
                action=NoAction()
            ))

        setup.start()
        sleep(SLEEP_WAIT)

        with self.assertRaises(RuntimeError):
            setup.configure()

        setup.cancel()

    def test_configure_when_configured(self):
        setup = BoboSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_1,
                action=NoAction()
            ))
        setup.configure()

        with self.assertRaises(RuntimeError):
            setup.configure()

    def test_configure_when_no_complex_event_definitions(self):
        setup = BoboSetup()

        with self.assertRaises(RuntimeError):
            setup.configure()

        self.assertFalse(setup.is_configured())

    def test_start_when_active(self):
        setup = BoboSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_1,
                action=NoAction()
            ))

        setup.start()
        sleep(SLEEP_WAIT)

        with self.assertRaises(RuntimeError):
            setup.start()

        setup.cancel()


class TestBoboSetupExtraSubscriber(unittest.TestCase):

    def test_subscribe_receiver_valid_data(self):
        setup = BoboSetup()
        sub = StubSubscriberSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_1,
                action=NoAction()
            ))

        setup.config_receiver(StrDictValidator())
        setup.subscribe_receiver(sub)
        setup.configure()

        receiver = setup.get_receiver()
        receiver.setup()

        receiver.add_data(DATA_DICT_A)
        receiver.loop()

        self.assertIsInstance(sub.receiver_event[0], PrimitiveEvent)

    def test_subscribe_receiver_invalid_data(self):
        setup = BoboSetup()
        sub = StubSubscriberSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_1,
                action=NoAction()
            ))

        setup.config_receiver(StrDictValidator())
        setup.subscribe_receiver(sub)
        setup.configure()

        receiver = setup.get_receiver()
        receiver.setup()

        receiver.add_data(VALUE_A)
        receiver.loop()

        self.assertEqual(VALUE_A, sub.invalid_data[0])

    def test_subscribe_decider_composite(self):
        setup = BoboSetup()
        sub = StubSubscriberSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_1,
                action=NoAction()
            ))

        setup.subscribe_decider(NAME_NFA_A, sub)
        setup.configure()

        decider = setup.get_decider()
        decider.setup()

        c_event = CompositeEvent(
            timestamp=EpochNSClock.generate_timestamp(),
            name=NAME_NFA_A,
            history=BoboHistory(),
            data={})

        decider.on_handler_final(NAME_NFA_A, RUN_ID_A, c_event)

        self.assertEqual(c_event, sub.decider_complex_event[0])

    def test_subscribe_producer_composite_accepted(self):
        setup = BoboSetup()
        sub = StubSubscriberSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_1,
                action=NoAction()
            ))

        setup.subscribe_producer(NAME_NFA_A, sub)
        setup.configure()

        producer = setup.get_producer()
        producer.setup()

        c_event = CompositeEvent(
            timestamp=EpochNSClock.generate_timestamp(),
            name=NAME_NFA_A,
            history=BoboHistory(),
            data={})

        producer.on_decider_complex_event(c_event)
        producer.loop()

        self.assertEqual(c_event, sub.accepted_producer_event[0])

    def test_subscribe_producer_composite_rejected(self):
        setup = BoboSetup()
        sub = StubSubscriberSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_1,
                action=NoAction()
            ))

        # this rejects all events passed to Producer
        setup.config_producer(NoAction(bool_return=False))

        setup.subscribe_producer(NAME_NFA_A, sub)
        setup.configure()

        producer = setup.get_producer()
        producer.setup()

        c_event = CompositeEvent(
            timestamp=EpochNSClock.generate_timestamp(),
            name=NAME_NFA_A,
            history=BoboHistory(),
            data={})

        producer.on_decider_complex_event(c_event)
        producer.loop()

        self.assertEqual(c_event, sub.rejected_producer_event[0])

    def test_subscribe_producer_action(self):
        setup = BoboSetup()
        sub = StubSubscriberSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_1,
                action=NoAction()
            ))

        setup.subscribe_producer(NAME_NFA_A, sub)
        setup.configure()

        producer = setup.get_producer()
        producer.setup()

        a_event = NoAction().execute(
            CompositeEvent(
                timestamp=EpochNSClock.generate_timestamp(),
                name=NAME_NFA_A,
                history=BoboHistory(),
                data={}))

        producer.on_action_attempt(a_event)
        producer.loop()

        self.assertEqual(a_event, sub.producer_action[0])

    def test_subscribe_forward_composite_success(self):
        setup = BoboSetup()
        sub = StubSubscriberSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_1,
                action=NoAction()
            ))

        setup.subscribe_forwarder(sub)
        setup.configure()

        forwarder = setup.get_forwarder()
        forwarder.setup()

        c_event = CompositeEvent(
            timestamp=EpochNSClock.generate_timestamp(),
            name=NAME_NFA_A,
            history=BoboHistory(),
            data={})

        forwarder.on_accepted_producer_event(c_event)
        forwarder.loop()

        self.assertEqual(c_event, sub.forwarder_success_event[0])

    def test_subscribe_forward_composite_failure(self):
        setup = BoboSetup()
        sub = StubSubscriberSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_1,
                action=NoAction()
            ))

        # this rejects all events passed to Forwarder
        setup.config_forwarder(NoAction(bool_return=False))

        setup.subscribe_forwarder(sub)
        setup.configure()

        forwarder = setup.get_forwarder()
        forwarder.setup()

        c_event = CompositeEvent(
            timestamp=EpochNSClock.generate_timestamp(),
            name=NAME_NFA_A,
            history=BoboHistory(),
            data={})

        forwarder.on_accepted_producer_event(c_event)
        forwarder.loop()

        self.assertEqual(c_event, sub.forwarder_failure_event[0])

    def test_subscribe_forward_action_success(self):
        setup = BoboSetup()
        sub = StubSubscriberSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_1,
                action=NoAction()
            ))

        setup.subscribe_forwarder(sub)
        setup.configure()

        forwarder = setup.get_forwarder()
        forwarder.setup()

        a_event = NoAction().execute(
            CompositeEvent(
                timestamp=EpochNSClock.generate_timestamp(),
                name=NAME_NFA_A,
                history=BoboHistory(),
                data={}))

        forwarder.on_producer_action(a_event)
        forwarder.loop()

        self.assertEqual(a_event, sub.forwarder_success_event[0])

    def test_subscribe_forward_action_failure(self):
        setup = BoboSetup()
        sub = StubSubscriberSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_1,
                action=NoAction()
            ))

        # this rejects all events passed to Forwarder
        setup.config_forwarder(NoAction(bool_return=False))

        setup.subscribe_forwarder(sub)
        setup.configure()

        forwarder = setup.get_forwarder()
        forwarder.setup()

        a_event = NoAction().execute(
            CompositeEvent(
                timestamp=EpochNSClock.generate_timestamp(),
                name=NAME_NFA_A,
                history=BoboHistory(),
                data={}))

        forwarder.on_producer_action(a_event)
        forwarder.loop()

        self.assertEqual(a_event, sub.forwarder_failure_event[0])


class TestBoboSetupDistributed(unittest.TestCase):

    def test_get_distributed_configured_but_not_distributed(self):
        setup = BoboSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_1,
                action=NoAction()
            ))
        setup.configure()

        with self.assertRaises(RuntimeError):
            setup.get_distributed()

    def test_on_sync(self):
        setup = BoboSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_4,
                action=NoAction()
            ))

        setup.config_null_data(
            delay_sec=NULL_DATA_DELAY,
            null_data=BoboNullDataStatic(DATA_DICT_A))

        setup.config_distributed(
            exchange_name=EXCHANGE_NAME,
            user_name=USER_NAME,
            parameters=parameters)

        setup.configure()
        self.assertFalse(setup.get_receiver().is_active())
        self.assertFalse(setup.get_decider().is_active())
        self.assertFalse(setup.get_producer().is_active())
        self.assertFalse(setup.get_forwarder().is_active())
        self.assertFalse(setup.get_null_data_generator().is_active())

        setup.on_sync()
        self.assertTrue(setup.get_receiver().is_active())
        self.assertTrue(setup.get_decider().is_active())
        self.assertTrue(setup.get_producer().is_active())
        self.assertTrue(setup.get_forwarder().is_active())
        self.assertTrue(setup.get_null_data_generator().is_active())


class TestBoboSetupScenarios(unittest.TestCase):

    def test_primitive_from_receiver_to_decider(self):
        setup = BoboSetup()

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_4
            ))
        setup.config_receiver(StrDictValidator())
        setup.configure()

        receiver = setup.get_receiver()
        receiver.setup()

        decider = setup.get_decider()
        decider.setup()

        receiver.add_data(DATA_DICT_A)
        receiver.loop()
        decider.loop()

        handlers = decider.get_all_handlers()
        self.assertEqual(NAME_NFA_A, handlers[0].nfa.name)

    def test_composite_from_decider_to_producer_recursive(self):
        setup = BoboSetup(recursive=True)

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_4
            ))
        setup.config_receiver(StrDictValidator())
        setup.configure()

        decider = setup.get_decider()
        decider.setup()

        producer = setup.get_producer()
        producer.setup()

        for event in [event_a, event_b, event_c, event_d]:
            decider.on_receiver_event(event)
            decider.loop()

        self.assertFalse(producer._event_queue.empty())

        producer.loop()
        handler = decider.get_all_handlers()[0]
        self.assertIsInstance(handler.get_all_recent()[0], CompositeEvent)

    def test_composite_from_decider_to_producer_not_recursive(self):
        setup = BoboSetup(recursive=False)

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_4
            ))
        setup.config_receiver(StrDictValidator())
        setup.configure()

        decider = setup.get_decider()
        decider.setup()

        producer = setup.get_producer()
        producer.setup()

        for event in [event_a, event_b, event_c, event_d]:
            decider.on_receiver_event(event)
            decider.loop()

        self.assertFalse(producer._event_queue.empty())

        producer.loop()
        handler = decider.get_all_handlers()[0]
        self.assertEqual(0, len(handler.get_all_recent()))

    def test_multi_composite_from_decider_to_producer_recursive(self):
        setup = BoboSetup(recursive=True, max_recent=2)

        nfa_names = [NAME_NFA_A, NAME_NFA_B, NAME_NFA_C]

        for nfa_name in nfa_names:
            setup.add_complex_event(
                event_def=BoboComplexEvent(
                    name=nfa_name,
                    pattern=stub_pattern_1,
                    action=NoAction()
                ))
        setup.config_receiver(StrDictValidator())
        setup.configure()

        decider = setup.get_decider()
        decider.setup()
        handlers = decider.get_all_handlers()
        self.assertEqual(3, len(handlers))

        producer = setup.get_producer()
        producer.setup()

        decider.on_receiver_event(event_a)

        for _ in range(len(nfa_names)):
            decider.loop()
            producer.loop()

        for handler in handlers:
            self.assertEqual(2, len(handler.get_all_recent()))

    def test_action_from_producer_to_decider_recursive(self):
        setup = BoboSetup(recursive=True)

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_4
            ))
        setup.config_receiver(StrDictValidator())
        setup.configure()

        decider = setup.get_decider()
        decider.setup()

        producer = setup.get_producer()
        producer.setup()

        a_event = NoAction().execute(
            CompositeEvent(
                timestamp=EpochNSClock.generate_timestamp(),
                name=NAME_NFA_A,
                history=BoboHistory(),
                data={}))

        producer.on_action_attempt(a_event)
        producer.loop()

        handler = decider.get_all_handlers()[0]
        self.assertEqual(a_event, handler.get_all_recent()[0])

    def test_action_from_producer_to_decider_not_recursive(self):
        setup = BoboSetup(recursive=False)

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_4
            ))
        setup.config_receiver(StrDictValidator())
        setup.configure()

        decider = setup.get_decider()
        decider.setup()

        producer = setup.get_producer()
        producer.setup()

        a_event = NoAction().execute(
            CompositeEvent(
                timestamp=EpochNSClock.generate_timestamp(),
                name=NAME_NFA_A,
                history=BoboHistory(),
                data={}))

        producer.on_action_attempt(a_event)
        producer.loop()

        handler = decider.get_all_handlers()[0]
        self.assertEqual(0, len(handler.get_all_recent()))

    def test_composite_from_producer_to_forwarder(self):
        setup = BoboSetup(recursive=True)

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_4
            ))
        setup.config_receiver(StrDictValidator())
        setup.configure()

        producer = setup.get_producer()
        producer.setup()

        forwarder = setup.get_forwarder()
        forwarder.setup()

        c_event = CompositeEvent(
            timestamp=EpochNSClock.generate_timestamp(),
            name=NAME_NFA_A,
            history=BoboHistory(),
            data={})

        producer.on_decider_complex_event(c_event)
        producer.loop()

        self.assertEqual(c_event, forwarder._event_queue.get_nowait())

    def test_action_from_producer_to_forwarder(self):
        setup = BoboSetup(recursive=True)

        setup.add_complex_event(
            event_def=BoboComplexEvent(
                name=NAME_NFA_A,
                pattern=stub_pattern_4
            ))
        setup.config_receiver(StrDictValidator())
        setup.configure()

        producer = setup.get_producer()
        producer.setup()

        forwarder = setup.get_forwarder()
        forwarder.setup()

        a_event = NoAction().execute(
            CompositeEvent(
                timestamp=EpochNSClock.generate_timestamp(),
                name=NAME_NFA_A,
                history=BoboHistory(),
                data={}))

        producer.on_action_attempt(a_event)
        producer.loop()

        self.assertEqual(a_event, forwarder._event_queue.get_nowait())
