import unittest

from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.actions.bobo_action import BoboAction
from bobocep.rules.events.action_event import ActionEvent
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.actions.action_subscriber import IActionSubscriber
from bobocep.rules.actions.no_action import NoAction


KEY_A = "key_a"
VALUE_A = "value_a"
DATA_A = {KEY_A: VALUE_A}
NAME_A = "name_a"
NAME_B = "name_b"
EXCEPTION_A = "exception_a"
DESCRIPTION_A = "description_a"
EVENT_ID_A = "event_id_a"


def generate_composite_event(name: str) -> CompositeEvent:
    return CompositeEvent(
        timestamp=EpochNSClock.generate_timestamp(),
        name=name,
        history=BoboHistory(),
        data={})


class StubBoboActionBool(BoboAction):

    def __init__(self, bool_return: bool) -> None:
        super().__init__()

        self.bool_return = bool_return
        self.events = []

    def _perform_action(self, event: CompositeEvent) -> bool:
        self.events.append(event)
        return self.bool_return


class StubBoboActionRuntimeException(BoboAction):

    def __init__(self, description: str) -> None:
        super().__init__()

        self.description = description
        self.events = []

    def _perform_action(self, event: CompositeEvent) -> bool:
        self.events.append(event)
        raise RuntimeError(self.description)


class StubBoboActionSubscriber(IActionSubscriber):

    def __init__(self) -> None:
        super().__init__()

        self.events = []

    def on_action_attempt(self, event: ActionEvent):
        self.events.append(event)


class TestBoboAction(unittest.TestCase):

    def test_execute_success(self):
        c_event_a = generate_composite_event(NAME_A)
        c_event_b = generate_composite_event(NAME_B)
        action = StubBoboActionBool(bool_return=True)

        # via execute
        self.assertTrue(action.execute(c_event_a).success)
        self.assertListEqual([c_event_a], action.events)

        # via subscription
        action.on_accepted_producer_event(c_event_b)
        self.assertListEqual([c_event_a, c_event_b], action.events)

    def test_execute_failure_by_false_return(self):
        c_event = generate_composite_event(NAME_A)
        action = StubBoboActionBool(bool_return=False)

        self.assertFalse(action.execute(c_event).success)
        self.assertListEqual([c_event], action.events)

    def test_execute_failure_by_exception(self):
        c_event = generate_composite_event(NAME_A)
        action = StubBoboActionRuntimeException(DESCRIPTION_A)

        self.assertFalse(action.execute(c_event).success)
        self.assertListEqual([c_event], action.events)

    def test_action_subscribe_unsubscribe(self):
        action = NoAction(bool_return=True)
        actionsub = StubBoboActionSubscriber()

        # subscribe
        action.subscribe(actionsub)
        c_event_a = generate_composite_event(NAME_A)
        action.execute(c_event_a)

        # event should cause ActionEvent to be passed to sub
        self.assertEqual(1, len(actionsub.events))
        self.assertIsInstance(actionsub.events[0], ActionEvent)
        self.assertEqual(c_event_a, actionsub.events[0].for_event)

        # unsubscribe
        action.unsubscribe(actionsub)
        action.execute(generate_composite_event(NAME_B))

        # no new ActionEvent
        self.assertEqual(1, len(actionsub.events))
