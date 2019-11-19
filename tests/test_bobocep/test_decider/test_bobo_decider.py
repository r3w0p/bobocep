import unittest
from time import sleep

from bobocep.decider.bobo_decider import BoboDecider
from bobocep.decider.buffers.shared_versioned_match_buffer import \
    SharedVersionedMatchBuffer
from bobocep.decider.decider_subscriber import IDeciderSubscriber
from bobocep.decider.handlers.bobo_nfa_handler import BoboNFAHandler
from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.actions.no_action import NoAction
from bobocep.rules.bobo_rule_builder import BoboRuleBuilder
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.rules.nfas.patterns.bobo_pattern import BoboPattern
from bobocep.rules.predicates.bobo_predicate_callable import \
    BoboPredicateCallable

NFA_NAME_A = "NFA_NAME_A"
NFA_NAME_B = "NFA_NAME_B"
NFA_NAME_C = "NFA_NAME_C"

RUN_ID_A = "run_id_a"
RUN_ID_B = "run_id_b"

LABEL_LAYER_A = 'layer_a'
LABEL_LAYER_B = 'layer_b'
LABEL_LAYER_C = 'layer_c'
LABEL_LAYER_D = 'layer_d'

EVENT_NAME_A = "event_name_a"
EVENT_NAME_B = "event_name_b"

event_a = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())
event_b = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())
event_c = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())

c_event_a = CompositeEvent(
    timestamp=EpochNSClock.generate_timestamp(),
    name=EVENT_NAME_A,
    history=BoboHistory())

c_event_b = CompositeEvent(
    timestamp=EpochNSClock.generate_timestamp(),
    name=EVENT_NAME_B,
    history=BoboHistory())

stub_predicate = BoboPredicateCallable(lambda e, h, r: True)

stub_pattern = BoboPattern() \
    .followed_by(LABEL_LAYER_A, stub_predicate) \
    .followed_by(LABEL_LAYER_B, stub_predicate) \
    .followed_by(LABEL_LAYER_C, stub_predicate) \
    .followed_by(LABEL_LAYER_D, stub_predicate)

stub_nfa_a = BoboRuleBuilder.nfa(NFA_NAME_A, stub_pattern)
stub_nfa_b = BoboRuleBuilder.nfa(NFA_NAME_B, stub_pattern)


def generate_handler_with_run():
    decider = BoboDecider()
    subscriber = DeciderSubscriber()

    handler = BoboNFAHandler(
        nfa=stub_nfa_a,
        buffer=SharedVersionedMatchBuffer(),
        max_recent=1)

    decider.add_nfa_handler(handler)
    decider.subscribe(handler.nfa.name, subscriber)
    decider.setup()

    # create initial run
    decider.on_receiver_event(event_a)
    decider.loop()

    run = list(handler.runs.values())[0]

    return decider, handler, run


class DeciderSubscriber(IDeciderSubscriber):

    def __init__(self) -> None:
        super().__init__()

        self.final = []

    def on_decider_complex_event(self, event: CompositeEvent) -> None:
        self.final.append(event)


class TestBoboDecider(unittest.TestCase):

    def test_add_nfa_handler(self):
        handler_a_1 = BoboNFAHandler(
            nfa=stub_nfa_a,
            buffer=SharedVersionedMatchBuffer())

        handler_a_2 = BoboNFAHandler(
            nfa=stub_nfa_a,
            buffer=SharedVersionedMatchBuffer())

        handler_b = BoboNFAHandler(
            nfa=stub_nfa_b,
            buffer=SharedVersionedMatchBuffer())

        decider = BoboDecider()

        # first handler
        decider.add_nfa_handler(handler_a_1)

        self.assertDictEqual(decider._nfa_handlers, {
            handler_a_1.nfa.name: handler_a_1
        })

        # reject handler with same name as one already in decider
        with self.assertRaises(RuntimeError):
            decider.add_nfa_handler(handler_a_2)

        # second handler with different name
        decider.add_nfa_handler(handler_b)

        self.assertDictEqual(decider._nfa_handlers, {
            handler_a_1.nfa.name: handler_a_1,
            handler_b.nfa.name: handler_b
        })

    def test_get_all_handlers(self):
        handler_a = BoboNFAHandler(
            nfa=stub_nfa_a,
            buffer=SharedVersionedMatchBuffer())

        handler_b = BoboNFAHandler(
            nfa=stub_nfa_b,
            buffer=SharedVersionedMatchBuffer())

        decider = BoboDecider()
        decider.add_nfa_handler(handler_a)
        decider.add_nfa_handler(handler_b)

        self.assertListEqual([handler_a, handler_b],
                             decider.get_all_handlers())

    def test_get_handler(self):
        handler_a = BoboNFAHandler(
            nfa=stub_nfa_a,
            buffer=SharedVersionedMatchBuffer())

        handler_b = BoboNFAHandler(
            nfa=stub_nfa_b,
            buffer=SharedVersionedMatchBuffer())

        decider = BoboDecider()
        decider.add_nfa_handler(handler_a)
        decider.add_nfa_handler(handler_b)

        self.assertEqual(handler_a, decider.get_handler(NFA_NAME_A))
        self.assertEqual(handler_b, decider.get_handler(NFA_NAME_B))
        self.assertIsNone(decider.get_handler(NFA_NAME_C))

    def test_receiver_event(self):
        decider = BoboDecider()

        # primitive
        decider.on_receiver_event(event_a)
        self.assertEqual(event_a, decider._event_queue.get_nowait())

        # composite
        decider.on_receiver_event(c_event_a)
        self.assertEqual(c_event_a, decider._event_queue.get_nowait())

        # action
        a_event = NoAction(bool_return=True).execute(c_event_b)
        decider.on_receiver_event(a_event)
        self.assertEqual(a_event, decider._event_queue.get_nowait())

    def test_producer_action(self):
        decider = BoboDecider()

        handler = BoboNFAHandler(
            nfa=stub_nfa_a,
            buffer=SharedVersionedMatchBuffer(),
            max_recent=2)

        decider.add_nfa_handler(handler)

        c_event_1 = CompositeEvent(
            timestamp=EpochNSClock.generate_timestamp(),
            name=handler.nfa.name,
            history=BoboHistory())
        sleep(0.1)
        c_event_2 = CompositeEvent(
            timestamp=EpochNSClock.generate_timestamp(),
            name=handler.nfa.name,
            history=BoboHistory())

        a_event_1 = NoAction(bool_return=True).execute(c_event_1)
        sleep(0.1)
        a_event_2 = NoAction(bool_return=True).execute(c_event_2)

        decider.on_producer_action(a_event_1)
        self.assertEqual([a_event_1], handler._recent)

        decider.on_producer_action(a_event_2)
        self.assertEqual([a_event_2, a_event_1], handler._recent)

    def test_final_subscribe_unsubscribe(self):
        decider = BoboDecider()
        subscriber = DeciderSubscriber()

        # no handler for nfa in decider yet
        with self.assertRaises(RuntimeError):
            decider.subscribe(stub_nfa_a.name, subscriber)

        handler_a = BoboNFAHandler(
            nfa=stub_nfa_a,
            buffer=SharedVersionedMatchBuffer())
        decider.add_nfa_handler(handler_a)

        # subscribe
        decider.subscribe(stub_nfa_a.name, subscriber)
        self.assertDictEqual(decider._subs, {
            stub_nfa_a.name: [subscriber]
        })

        decider.on_handler_final(
            nfa_name=NFA_NAME_A,
            run_id=RUN_ID_A,
            event=c_event_a
        )

        self.assertListEqual([c_event_a], subscriber.final)

        # unsubscribe
        decider.unsubscribe(stub_nfa_a.name, subscriber)
        self.assertDictEqual(decider._subs, {
            stub_nfa_a.name: []
        })

        decider.on_handler_final(
            nfa_name=NFA_NAME_B,
            run_id=RUN_ID_B,
            event=c_event_b
        )

        self.assertListEqual([c_event_a], subscriber.final)

    def test_loop(self):
        handler_a = BoboNFAHandler(
            nfa=stub_nfa_a,
            buffer=SharedVersionedMatchBuffer())

        p_event = PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp())

        # add handler and event
        decider = BoboDecider()
        decider.setup()
        decider.add_nfa_handler(handler_a)

        # test receiver event
        decider.on_receiver_event(p_event)
        decider.loop()

        # A new run should have been created in the handler
        self.assertEqual(1, len(handler_a.runs.values()))


class TestBoboDeciderDistInterfaces(unittest.TestCase):

    def test_dist_transition(self):
        decider, handler, run = generate_handler_with_run()

        # get next state
        transition = handler.nfa.transitions[run.current_state.name]
        next_state = handler.nfa.states[transition.state_names[0]]

        decider.on_dist_run_transition(
            nfa_name=handler.nfa.name,
            run_id=run.id,
            state_name_from=run.current_state.name,
            state_name_to=next_state.name,
            event=event_b
        )

        self.assertEqual(next_state.name,
                         run.current_state.name)

    def test_dist_transition_invalid_nfa_name(self):
        decider, handler, run = generate_handler_with_run()

        # get next state
        transition = handler.nfa.transitions[run.current_state.name]
        next_state = handler.nfa.states[transition.state_names[0]]

        with self.assertRaises(RuntimeError):
            decider.on_dist_run_transition(
                nfa_name=NFA_NAME_B,
                run_id=run.id,
                state_name_from=run.current_state.name,
                state_name_to=next_state.name,
                event=event_b
            )

    def test_dist_clone(self):
        decider, handler, run = generate_handler_with_run()

        # get next state
        transition = handler.nfa.transitions[run.current_state.name]
        next_state = handler.nfa.states[transition.state_names[0]]

        decider.on_dist_run_clone(
            nfa_name=handler.nfa.name,
            run_id=run.id,
            next_state_name=next_state.name,
            next_event=event_b
        )

        runs = list(handler.runs.values())
        run_clone = runs[0] if runs[0] is not run else runs[1]

        self.assertEqual(handler.nfa.start_state.name,
                         run.current_state.name)

        self.assertEqual(next_state.name,
                         run_clone.current_state.name)

    def test_dist_clone_invalid_nfa_name(self):
        decider, handler, run = generate_handler_with_run()

        # get next state
        transition = handler.nfa.transitions[run.current_state.name]
        next_state = handler.nfa.states[transition.state_names[0]]

        with self.assertRaises(RuntimeError):
            decider.on_dist_run_clone(
                nfa_name=NFA_NAME_B,
                run_id=run.id,
                next_state_name=next_state.name,
                next_event=event_b
            )

    def test_dist_halt(self):
        decider, handler, run = generate_handler_with_run()

        decider.on_dist_run_halt(
            nfa_name=handler.nfa.name,
            run_id=run.id
        )

        self.assertTrue(run.is_halted())

    def test_dist_halt_invalid_nfa_name(self):
        decider, handler, run = generate_handler_with_run()

        with self.assertRaises(RuntimeError):
            decider.on_dist_run_halt(
                nfa_name=NFA_NAME_B,
                run_id=run.id
            )

    def test_dist_final(self):
        decider, handler, run = generate_handler_with_run()

        sub = DeciderSubscriber()
        decider.subscribe(handler.nfa.name, sub)

        decider.on_dist_run_final(
            nfa_name=handler.nfa.name,
            run_id=run.id,
            event=c_event_a
        )

        self.assertTrue(run.is_final())
        self.assertEqual(0, len(handler.runs))

    def test_dist_final_invalid_nfa_name(self):
        decider, handler, run = generate_handler_with_run()

        sub = DeciderSubscriber()
        decider.subscribe(handler.nfa.name, sub)

        with self.assertRaises(RuntimeError):
            decider.on_dist_run_final(
                nfa_name=NFA_NAME_B,
                run_id=run.id,
                event=c_event_a
            )

    def test_dist_action(self):
        decider, handler, run = generate_handler_with_run()

        c_event = CompositeEvent(
            timestamp=EpochNSClock.generate_timestamp(),
            name=handler.nfa.name,
            history=BoboHistory())

        a_event = NoAction(bool_return=True).execute(c_event)
        decider.on_dist_action(a_event)

        self.assertListEqual([a_event], handler._recent)

    def test_dist_action_invalid_nfa_name(self):
        decider, handler, run = generate_handler_with_run()

        c_event = CompositeEvent(
            timestamp=EpochNSClock.generate_timestamp(),
            name=NFA_NAME_B,
            history=BoboHistory())

        a_event = NoAction(bool_return=True).execute(c_event)

        with self.assertRaises(RuntimeError):
            decider.on_dist_action(a_event)
