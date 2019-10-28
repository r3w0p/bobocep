from pika import ConnectionParameters

from bobocep.decider.bobo_decider import BoboDecider
from bobocep.setup.distributed.incoming.bobo_dist_incoming import \
    BoboDistIncoming
from bobocep.setup.distributed.outgoing.bobo_dist_outgoing import \
    BoboDistOutgoing
from bobocep.setup.task.bobo_task_thread import \
    BoboTaskThread


class BoboDistManager:
    """A manager for incoming and outgoing data that helps multiple
    :code:`bobocep` instances synchronise data between each other using an
    external message queue system.

    :param decider: The decider to which synchronisation will occur.
    :type decider: BoboDecider

    :param exchange_name: The exchange name to connect to on the external
                          message queue system.
    :type exchange_name: str

    :param user_id: The user ID to use on the external message queue system.
    :type user_id: str

    :param parameters: Parameters to connect to a message broker.
    :type parameters: ConnectionParameters

    :param delay: The delay for internal BoboTask threads, in seconds.
    :type delay: float

    :param max_sync_attempts: Maximum attempts to sync with other
                              :code:`bobocep` instances before giving up,
                              defaults to 3.
    :type max_sync_attempts: int, optional
    """

    def __init__(self,
                 decider: BoboDecider,
                 exchange_name: str,
                 user_id: str,
                 parameters: ConnectionParameters,
                 delay: float,
                 max_sync_attempts: int = 3) -> None:
        super().__init__()

        self.parameters = parameters

        self.outgoing = BoboDistOutgoing(
            decider=decider,
            exchange_name=exchange_name,
            user_id=user_id,
            parameters=parameters,
            max_sync_attempts=max_sync_attempts
        )

        self.incoming = BoboDistIncoming(
            outgoing=self.outgoing,
            decider=decider,
            exchange_name=exchange_name,
            user_id=user_id,
            parameters=parameters
        )

        self._incoming_thread = BoboTaskThread(self.incoming, delay)
        self._outgoing_thread = BoboTaskThread(self.outgoing, delay)

    def start(self):
        """Run the manager threads."""

        self._incoming_thread.start()
        self._outgoing_thread.start()

    def cancel(self):
        """Cancel the manager threads."""

        self._incoming_thread.cancel()
        self._outgoing_thread.cancel()
