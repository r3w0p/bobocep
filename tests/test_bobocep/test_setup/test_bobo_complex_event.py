import unittest

from bobocep.rules.actions.no_action import NoAction
from bobocep.rules.nfas.patterns.bobo_pattern import BoboPattern
from bobocep.setup.bobo_complex_event import \
    BoboComplexEvent


class TestBoboComplexEvent(unittest.TestCase):

    def test_constructor(self):
        name = "evdef_name"
        pattern = BoboPattern()
        action = NoAction()

        evdef = BoboComplexEvent(name=name,
                                 pattern=pattern,
                                 action=action)

        self.assertEqual(name, evdef.name)
        self.assertEqual(pattern, evdef.pattern)
        self.assertEqual(action, evdef.action)

    def test_constructor_actions_is_none(self):
        name = "evdef_name"
        pattern = BoboPattern()
        action = None

        evdef = BoboComplexEvent(name=name,
                                 pattern=pattern,
                                 action=action)

        self.assertEqual(name, evdef.name)
        self.assertEqual(pattern, evdef.pattern)
        self.assertIsNone(evdef.action)
