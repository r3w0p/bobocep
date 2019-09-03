import unittest

from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.bobo_rule_builder import BoboRuleBuilder
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.primitive_event import PrimitiveEvent


class TestBoboRuleBuilder(unittest.TestCase):

    def test_primitive(self):
        # Primitive event data
        p_timestamp = EpochNSClock.generate_timestamp()
        p_data = "p_data"
        p_id = "p_id_123"

        # Create dict representation of primitive event
        p_dict = {
            PrimitiveEvent.TIMESTAMP: p_timestamp,
            PrimitiveEvent.DATA: p_data,
            PrimitiveEvent.ID: p_id
        }

        # Build actual primitive event from dict
        p_event = BoboRuleBuilder.primitive(p_dict)

        self.assertEqual(p_event.timestamp, p_timestamp)
        self.assertEqual(p_event.data, p_data)
        self.assertEqual(p_event.id, p_id)

    def test_primitive_none(self):
        p_timestamp = EpochNSClock.generate_timestamp()
        p_data = "p_data"
        p_id = "p_id_123"

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.primitive({
                PrimitiveEvent.TIMESTAMP: None,
                PrimitiveEvent.DATA: p_data,
                PrimitiveEvent.ID: p_id
            })

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.primitive({
                PrimitiveEvent.TIMESTAMP: p_timestamp,
                PrimitiveEvent.DATA: None,
                PrimitiveEvent.ID: p_id
            })

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.primitive({
                PrimitiveEvent.TIMESTAMP: p_timestamp,
                PrimitiveEvent.DATA: p_data,
                PrimitiveEvent.ID: None
            })

    def test_composite(self):
        # Composite event data
        c_timestamp = EpochNSClock.generate_timestamp()
        c_name = "c_name"
        c_data = "c_data"
        c_id = "c_id_123"

        # Primitive event used in composite event's history
        p_timestamp = EpochNSClock.generate_timestamp()
        p_data = "p_data"
        p_hist = "p_hist"
        p_id = "p_id_123"

        # Create dict representation of composite event
        c_dict = {
            CompositeEvent.TIMESTAMP: c_timestamp,
            CompositeEvent.NAME: c_name,
            CompositeEvent.HISTORY: {
                p_hist: [{
                    PrimitiveEvent.TIMESTAMP: p_timestamp,
                    PrimitiveEvent.DATA: p_data,
                    PrimitiveEvent.ID: p_id
                }]
            },
            CompositeEvent.DATA: c_data,
            CompositeEvent.ID: c_id
        }

        # Check composite event
        c_event = BoboRuleBuilder.composite(c_dict)

        self.assertEqual(c_event.timestamp, c_timestamp)
        self.assertEqual(c_event.name, c_name)
        self.assertEqual(c_event.data, c_data)
        self.assertEqual(c_event.id, c_id)

        # Check primitive event in history
        p_event = c_event.history.events[p_hist][0]

        self.assertEqual(p_event.timestamp, p_timestamp)
        self.assertEqual(p_event.data, p_data)
        self.assertEqual(p_event.id, p_id)

    def test_composite_none(self):
        c_timestamp = EpochNSClock.generate_timestamp()
        c_name = "c_name"
        c_history = {}
        c_data = "c_data"
        c_id = "c_id"

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.composite({
                CompositeEvent.TIMESTAMP: None,
                CompositeEvent.NAME: c_name,
                CompositeEvent.HISTORY: c_history,
                CompositeEvent.DATA: c_data,
                CompositeEvent.ID: c_id
            })

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.composite({
                CompositeEvent.TIMESTAMP: c_timestamp,
                CompositeEvent.NAME: None,
                CompositeEvent.HISTORY: c_history,
                CompositeEvent.DATA: c_data,
                CompositeEvent.ID: c_id
            })

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.composite({
                CompositeEvent.TIMESTAMP: c_timestamp,
                CompositeEvent.NAME: c_name,
                CompositeEvent.HISTORY: None,
                CompositeEvent.DATA: c_data,
                CompositeEvent.ID: c_id
            })

        with self.assertRaises(RuntimeError):
            BoboRuleBuilder.composite({
                CompositeEvent.TIMESTAMP: c_timestamp,
                CompositeEvent.NAME: c_name,
                CompositeEvent.HISTORY: c_history,
                CompositeEvent.DATA: c_data,
                CompositeEvent.ID: None
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
                PrimitiveEvent.ID: p1_id
            }],
            p2_hist: [{
                PrimitiveEvent.TIMESTAMP: p2_timestamp,
                PrimitiveEvent.DATA: p2_data,
                PrimitiveEvent.ID: p2_id
            }]
        }

        history = BoboRuleBuilder.history(h_dict)

        p1_event = history.events[p1_hist][0]

        self.assertEqual(p1_event.timestamp, p1_timestamp)
        self.assertEqual(p1_event.data, p1_data)
        self.assertEqual(p1_event.id, p1_id)

        p2_event = history.events[p2_hist][0]

        self.assertEqual(p2_event.timestamp, p2_timestamp)
        self.assertEqual(p2_event.data, p2_data)
        self.assertEqual(p2_event.id, p2_id)

    def test_event_primitive(self):
        # Primitive event data
        p_timestamp = EpochNSClock.generate_timestamp()
        p_data = "p_data"
        p_id = "p_id_123"

        # Create dict representation of primitive event
        p_dict = {
            PrimitiveEvent.TIMESTAMP: p_timestamp,
            PrimitiveEvent.DATA: p_data,
            PrimitiveEvent.ID: p_id
        }

        self.assertTrue(isinstance(BoboRuleBuilder.event(p_dict),
                                   PrimitiveEvent))

    def test_event_composite(self):
        # Composite event data
        c_timestamp = EpochNSClock.generate_timestamp()
        c_name = "c_name"
        c_data = "c_data"
        c_id = "c_id_123"

        # Create dict representation of composite event
        c_dict = {
            CompositeEvent.TIMESTAMP: c_timestamp,
            CompositeEvent.NAME: c_name,
            CompositeEvent.HISTORY: {},
            CompositeEvent.DATA: c_data,
            CompositeEvent.ID: c_id
        }

        self.assertTrue(isinstance(BoboRuleBuilder.event(c_dict),
                                   CompositeEvent))
