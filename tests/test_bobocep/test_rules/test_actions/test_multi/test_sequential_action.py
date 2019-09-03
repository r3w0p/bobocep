import unittest

from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.actions.multi.sequential_action import SequentialAction
from bobocep.rules.actions.no_action import NoAction
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory

ACTION_TRUE = NoAction(bool_return=True)
ACTION_FALSE = NoAction(bool_return=False)


def generate_composite_event() -> CompositeEvent:
    return CompositeEvent(
        timestamp=EpochNSClock.generate_timestamp(),
        name="name",
        history=BoboHistory(),
        data={})


class TestSequentialAction(unittest.TestCase):

    def test_any_success_all_pass(self):
        seq = SequentialAction(
            actions=[
                ACTION_TRUE,
                ACTION_TRUE,
                ACTION_TRUE],
            all_success=False,
            early_stop=False)

        self.assertTrue(seq.perform_action(generate_composite_event()))

    def test_any_success_some_pass(self):
        seq = SequentialAction(
            actions=[
                ACTION_FALSE,
                ACTION_TRUE,
                ACTION_TRUE],
            all_success=False,
            early_stop=False)

        self.assertTrue(seq.perform_action(generate_composite_event()))

    def test_any_success_none_pass(self):
        seq = SequentialAction(
            actions=[
                ACTION_FALSE,
                ACTION_FALSE,
                ACTION_FALSE],
            all_success=False,
            early_stop=False)

        self.assertFalse(seq.perform_action(generate_composite_event()))

    def test_any_success_early_stop(self):
        seq = SequentialAction(
            actions=[
                ACTION_FALSE,
                ACTION_TRUE,
                ACTION_TRUE],
            all_success=False,
            early_stop=True)

        self.assertFalse(seq.perform_action(generate_composite_event()))

    def test_all_success_all_pass(self):
        seq = SequentialAction(
            actions=[
                ACTION_TRUE,
                ACTION_TRUE,
                ACTION_TRUE],
            all_success=True,
            early_stop=False)

        self.assertTrue(seq.perform_action(generate_composite_event()))

    def test_all_success_some_pass(self):
        seq = SequentialAction(
            actions=[
                ACTION_FALSE,
                ACTION_TRUE,
                ACTION_TRUE],
            all_success=True,
            early_stop=False)

        self.assertFalse(seq.perform_action(generate_composite_event()))

    def test_all_success_none_pass(self):
        seq = SequentialAction(
            actions=[
                ACTION_FALSE,
                ACTION_FALSE,
                ACTION_FALSE],
            all_success=True,
            early_stop=False)

        self.assertFalse(seq.perform_action(generate_composite_event()))

    def test_all_success_early_stop(self):
        seq = SequentialAction(
            actions=[
                ACTION_FALSE,
                ACTION_TRUE,
                ACTION_TRUE],
            all_success=True,
            early_stop=True)

        self.assertFalse(seq.perform_action(generate_composite_event()))
