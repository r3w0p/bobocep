import unittest

from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.bobo_rule_builder import BoboRuleBuilder
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.events.action_event import ActionEvent


KEY_A = "key_a"
VALUE_A = "value_a"
DATA_A = {KEY_A: VALUE_A}
NAME_A = "name_a"
NAME_B = "name_b"
LABEL_A = "label_a"
EXCEPTION_A = "exception_a"
DESCRIPTION_A = "description_a"
EVENT_ID_A = "event_id_a"
EVENT_ID_B = "event_id_b"


class TestBoboRuleBuilder(unittest.TestCase):

    def test_primitive(self):
        # primitive event data
        p_timestamp = EpochNSClock.generate_timestamp()
        p_data = DATA_A
        p_id = EVENT_ID_A

        # Create dict representation of primitive event
        p_dict = {
            PrimitiveEvent.TIMESTAMP: p_timestamp,
            PrimitiveEvent.DATA: p_data,
            PrimitiveEvent.EVENT_ID: p_id
        }

        # Build actual primitive event from dict
        p_event_1 = BoboRuleBuilder.primitive(p_dict)
        p_event_2 = BoboRuleBuilder.event(p_dict)

        for p_event in [p_event_1, p_event_2]:
            self.assertEqual(p_event.timestamp, p_timestamp)
            self.assertEqual(p_event.data, p_data)
            self.assertEqual(p_event.event_id, p_id)

    def test_primitive_none(self):
        p_timestamp = EpochNSClock.generate_timestamp()
        p_data = DATA_A
        p_id = EVENT_ID_A

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.primitive({
                PrimitiveEvent.TIMESTAMP: None,
                PrimitiveEvent.DATA: p_data,
                PrimitiveEvent.EVENT_ID: p_id
            })

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.primitive({
                PrimitiveEvent.TIMESTAMP: p_timestamp,
                PrimitiveEvent.DATA: None,
                PrimitiveEvent.EVENT_ID: p_id
            })

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.primitive({
                PrimitiveEvent.TIMESTAMP: p_timestamp,
                PrimitiveEvent.DATA: p_data,
                PrimitiveEvent.EVENT_ID: None
            })

    def test_composite(self):
        # composite event data
        c_timestamp = EpochNSClock.generate_timestamp()
        c_name = NAME_A
        c_data = DATA_A
        c_id = EVENT_ID_A

        # primitive event used in composite event's history
        p_timestamp = EpochNSClock.generate_timestamp()
        p_data = NAME_B
        p_label = LABEL_A
        p_id = EVENT_ID_B

        # create dict representation of composite event
        c_dict = {
            CompositeEvent.TIMESTAMP: c_timestamp,
            CompositeEvent.NAME: c_name,
            CompositeEvent.HISTORY: {
                p_label: [{
                    PrimitiveEvent.TIMESTAMP: p_timestamp,
                    PrimitiveEvent.DATA: p_data,
                    PrimitiveEvent.EVENT_ID: p_id
                }]
            },
            CompositeEvent.DATA: c_data,
            CompositeEvent.EVENT_ID: c_id
        }

        # check composite event
        c_event_1 = BoboRuleBuilder.composite(c_dict)
        c_event_2 = BoboRuleBuilder.event(c_dict)

        for c_event in [c_event_1, c_event_2]:
            self.assertEqual(c_event.timestamp, c_timestamp)
            self.assertEqual(c_event.name, c_name)
            self.assertEqual(c_event.data, c_data)
            self.assertEqual(c_event.event_id, c_id)

            # Check primitive event in history
            p_event = c_event.history.events[p_label][0]

            self.assertEqual(p_event.timestamp, p_timestamp)
            self.assertEqual(p_event.data, p_data)
            self.assertEqual(p_event.event_id, p_id)

    def test_composite_none(self):
        c_timestamp = EpochNSClock.generate_timestamp()
        c_name = NAME_A
        c_history = {}
        c_data = DATA_A
        c_id = EVENT_ID_A

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.composite({
                CompositeEvent.TIMESTAMP: None,
                CompositeEvent.NAME: c_name,
                CompositeEvent.HISTORY: c_history,
                CompositeEvent.DATA: c_data,
                CompositeEvent.EVENT_ID: c_id
            })

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.composite({
                CompositeEvent.TIMESTAMP: c_timestamp,
                CompositeEvent.NAME: None,
                CompositeEvent.HISTORY: c_history,
                CompositeEvent.DATA: c_data,
                CompositeEvent.EVENT_ID: c_id
            })

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.composite({
                CompositeEvent.TIMESTAMP: c_timestamp,
                CompositeEvent.NAME: c_name,
                CompositeEvent.HISTORY: None,
                CompositeEvent.DATA: c_data,
                CompositeEvent.EVENT_ID: c_id
            })

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.composite({
                CompositeEvent.TIMESTAMP: c_timestamp,
                CompositeEvent.NAME: c_name,
                CompositeEvent.HISTORY: c_history,
                CompositeEvent.DATA: c_data,
                CompositeEvent.EVENT_ID: None
            })

    def test_action(self):
        # action event data
        a_timestamp = EpochNSClock.generate_timestamp()
        a_name = NAME_A
        a_success = True
        a_for_event = CompositeEvent(
            timestamp=EpochNSClock.generate_timestamp(),
            name=NAME_B,
            history=BoboHistory(),
            data={}
        )
        a_exception = EXCEPTION_A
        a_description = DESCRIPTION_A
        a_data = DATA_A
        a_event_id = EVENT_ID_A

        # create dict representation of action event
        a_dict = {
            ActionEvent.TIMESTAMP: a_timestamp,
            ActionEvent.NAME: a_name,
            ActionEvent.SUCCESS: a_success,
            ActionEvent.FOR_EVENT: a_for_event.to_dict(),
            ActionEvent.EXCEPTION: a_exception,
            ActionEvent.DESCRIPTION: a_description,
            ActionEvent.DATA: a_data,
            ActionEvent.EVENT_ID: a_event_id
        }

        # build actual action event from dict
        a_event_1 = BoboRuleBuilder.action(a_dict)
        a_event_2 = BoboRuleBuilder.event(a_dict)

        for a_event in [a_event_1, a_event_2]:
            self.assertEqual(a_event.timestamp, a_timestamp)
            self.assertEqual(a_event.name, a_name)
            self.assertEqual(a_event.success, a_success)
            self.assertEqual(a_event.exception, a_exception)
            self.assertEqual(a_event.description, a_description)
            self.assertDictEqual(a_event.data, a_data)
            self.assertEqual(a_event.event_id, a_event_id)

            c_event = a_event.for_event
            self.assertIsInstance(c_event, CompositeEvent)
            self.assertEqual(c_event.timestamp, a_for_event.timestamp)
            self.assertEqual(c_event.name, a_for_event.name)
            self.assertIsNone(c_event.history.first)
            self.assertDictEqual(c_event.data, a_for_event.data)
            self.assertEqual(c_event.event_id, a_for_event.event_id)

    def test_action_none(self):
        # action event data
        a_timestamp = EpochNSClock.generate_timestamp()
        a_name = NAME_A
        a_success = True
        a_for_event = CompositeEvent(
            timestamp=EpochNSClock.generate_timestamp(),
            name=NAME_B,
            history=BoboHistory(),
            data={}
        )
        a_exception = EXCEPTION_A
        a_description = DESCRIPTION_A
        a_data = DATA_A
        a_event_id = EVENT_ID_A

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.action({
                ActionEvent.TIMESTAMP: None,
                ActionEvent.NAME: a_name,
                ActionEvent.SUCCESS: a_success,
                ActionEvent.FOR_EVENT: a_for_event.to_dict(),
                ActionEvent.EXCEPTION: a_exception,
                ActionEvent.DESCRIPTION: a_description,
                ActionEvent.DATA: a_data,
                ActionEvent.EVENT_ID: a_event_id
            })

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.action({
                ActionEvent.TIMESTAMP: a_timestamp,
                ActionEvent.NAME: None,
                ActionEvent.SUCCESS: a_success,
                ActionEvent.FOR_EVENT: a_for_event.to_dict(),
                ActionEvent.EXCEPTION: a_exception,
                ActionEvent.DESCRIPTION: a_description,
                ActionEvent.DATA: a_data,
                ActionEvent.EVENT_ID: a_event_id
            })

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.action({
                ActionEvent.TIMESTAMP: a_timestamp,
                ActionEvent.NAME: a_name,
                ActionEvent.SUCCESS: None,
                ActionEvent.FOR_EVENT: a_for_event.to_dict(),
                ActionEvent.EXCEPTION: a_exception,
                ActionEvent.DESCRIPTION: a_description,
                ActionEvent.DATA: a_data,
                ActionEvent.EVENT_ID: a_event_id
            })

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.action({
                ActionEvent.TIMESTAMP: a_timestamp,
                ActionEvent.NAME: a_name,
                ActionEvent.SUCCESS: a_success,
                ActionEvent.FOR_EVENT: None,
                ActionEvent.EXCEPTION: a_exception,
                ActionEvent.DESCRIPTION: a_description,
                ActionEvent.DATA: a_data,
                ActionEvent.EVENT_ID: a_event_id
            })

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.action({
                ActionEvent.TIMESTAMP: a_timestamp,
                ActionEvent.NAME: a_name,
                ActionEvent.SUCCESS: a_success,
                ActionEvent.FOR_EVENT: a_for_event.to_dict(),
                ActionEvent.EXCEPTION: a_exception,
                ActionEvent.DESCRIPTION: a_description,
                ActionEvent.DATA: a_data,
                ActionEvent.EVENT_ID: None
            })

    def test_history(self):
        p1_hist = "p1_hist"
        p2_hist = "p2_hist"

        # Primitive events used in history
        p1_timestamp = EpochNSClock.generate_timestamp()
        p1_data = "p1_data"

        p2_timestamp = EpochNSClock.generate_timestamp()
        p2_data = "p2_data"

        p1_id = "p1_id_123"
        p2_id = "p2_id_123"

        h_dict = {
            p1_hist: [{
                PrimitiveEvent.TIMESTAMP: p1_timestamp,
                PrimitiveEvent.DATA: p1_data,
                PrimitiveEvent.EVENT_ID: p1_id
            }],
            p2_hist: [{
                PrimitiveEvent.TIMESTAMP: p2_timestamp,
                PrimitiveEvent.DATA: p2_data,
                PrimitiveEvent.EVENT_ID: p2_id
            }]
        }

        history = BoboRuleBuilder.history(h_dict)

        p1_event = history.events[p1_hist][0]

        self.assertEqual(p1_event.timestamp, p1_timestamp)
        self.assertEqual(p1_event.data, p1_data)
        self.assertEqual(p1_event.event_id, p1_id)

        p2_event = history.events[p2_hist][0]

        self.assertEqual(p2_event.timestamp, p2_timestamp)
        self.assertEqual(p2_event.data, p2_data)
        self.assertEqual(p2_event.event_id, p2_id)
