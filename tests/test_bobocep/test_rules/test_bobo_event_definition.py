import unittest

from bobocep.rules.actions.no_action import NoAction
from bobocep.rules.nfas.patterns.bobo_pattern import BoboPattern
from bobocep.setup.bobo_complex_event import \
    BoboComplexEvent


class TestBoboEventDefinition(unittest.TestCase):

    def test_constructor_one_action(self):
        name = "evdef_name"
        pattern = BoboPattern()
        actions = [NoAction()]

        evdef = BoboComplexEvent(name=name,
                                 pattern=pattern,
                                 actions=actions)

        self.assertEqual(name, evdef.name)
        self.assertEqual(pattern, evdef.pattern)
        self.assertListEqual(actions, evdef.actions)

    def test_constructor_actions_is_none(self):
        name = "evdef_name"
        pattern = BoboPattern()
        actions = None

        evdef = BoboComplexEvent(name=name,
                                 pattern=pattern,
                                 actions=actions)

        self.assertEqual(name, evdef.name)
        self.assertEqual(pattern, evdef.pattern)
        self.assertListEqual([], evdef.actions)
