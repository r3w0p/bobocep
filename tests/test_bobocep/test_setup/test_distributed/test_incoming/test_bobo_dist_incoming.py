import unittest

from bobocep.decider.bobo_decider import BoboDecider
from bobocep.rules.events.action_event import ActionEvent
from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.setup.distributed.bobo_dist_manager import BoboDistManager
from bobocep.setup.distributed.incoming.bobo_dist_incoming import \
    BoboDistIncoming
from bobocep.setup.distributed.incoming.dist_incoming_subscriber import \
    IDistIncomingSubscriber

EXCHANGE_NAME = "test_exchange_name"
USER_ID = "test_user_id"
HOST_NAME = "127.0.0.1"
DELAY = 0.5


def setup_incoming() -> BoboDistIncoming:
    return BoboDistManager(
        decider=BoboDecider(),
        exchange_name=EXCHANGE_NAME,
        user_id=USER_ID,
        host_name=HOST_NAME,
        delay=DELAY
    ).incoming


class StubDistIncomingSubscriber(IDistIncomingSubscriber):

    def __init__(self) -> None:
        super().__init__()

    def on_dist_run_transition(self, nfa_name: str, run_id: str,
                               state_name_from: str, state_name_to: str,
                               event: BoboEvent) -> None:
        """"""

    def on_dist_run_clone(self, nfa_name: str, run_id: str,
                          next_state_name: str, next_event: BoboEvent) -> None:
        """"""

    def on_dist_run_halt(self, nfa_name: str, run_id: str) -> None:
        """"""

    def on_dist_run_final(self, nfa_name: str, run_id: str,
                          history: BoboHistory) -> None:
        """"""

    def on_dist_action(self, event: ActionEvent) -> None:
        """"""


class TestBoboDistIncoming(unittest.TestCase):

    def test_subscribe_unsubscribe(self):
        incoming = setup_incoming()
        sub = StubDistIncomingSubscriber()

        self.assertListEqual([], incoming._subs)

        incoming.subscribe(sub)
        self.assertListEqual([sub], incoming._subs)

        incoming.unsubscribe(sub)
        self.assertListEqual([], incoming._subs)

    def test_sync_then_cancel(self):
        incoming = setup_incoming()
        self.assertFalse(incoming._is_synced)

        incoming.on_sync()
        self.assertTrue(incoming._is_synced)

        incoming.cancel()
        self.assertFalse(incoming._is_synced)
