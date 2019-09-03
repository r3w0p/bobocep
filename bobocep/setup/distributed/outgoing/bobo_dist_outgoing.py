import json
from queue import Queue
from time import time
from uuid import uuid4

import pika

import bobocep.setup.distributed.bobo_dist_constants as bdc
from bobocep.decider.dist_decider import DistDecider
from bobocep.decider.handlers.nfa_handler_subscriber import \
    INFAHandlerSubscriber
from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.setup.distributed.incoming.dist_incoming_subscriber import \
    IDistIncomingSubscriber
from bobocep.setup.distributed.outgoing.dist_outgoing_subscriber import \
    IDistOutgoingSubscriber
from bobocep.setup.task.bobo_task import BoboTask


class BoboDistOutgoing(BoboTask,
                       INFAHandlerSubscriber,
                       IDistIncomingSubscriber):
    """Handles outgoing synchronisation data for other :code:`bobocep`
    instances.

    :param decider: The decider to which synchronisation will occur.
    :type decider: DistDecider

    :param exchange_name: The exchange name to connect to on the external
                          message queue system.
    :type exchange_name: str

    :param user_id: The user ID to use on the external message queue system.
    :type user_id: str

    :param host_name: The host name of the external message queue system.
    :type host_name: str
    """

    def __init__(self,
                 decider: DistDecider,
                 exchange_name: str,
                 user_id: str,
                 host_name: str,
                 max_sync_attempts: int = 3) -> None:
        super().__init__()

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host_name))
        channel = connection.channel()

        self.decider = decider
        self.exchange_name = exchange_name
        self.user_id = user_id
        self.sync_id = None
        self.host_name = host_name
        self.max_sync_attempts = max_sync_attempts

        self._queue_transition = Queue()
        self._queue_clone = Queue()
        self._queue_halt = Queue()
        self._queue_final = Queue()

        self._subs = []
        self._connection = connection
        self._channel = channel
        self._is_synced = False
        self._sync_response = None

    def _setup(self) -> None:
        self._sync()

    def _loop(self) -> None:
        if self._is_synced:
            self._send_events(self._queue_transition, bdc.TRANSITION)
            self._send_events(self._queue_clone, bdc.CLONE)
            self._send_events(self._queue_halt, bdc.HALT)
            self._send_events(self._queue_final, bdc.FINAL)

    def _cancel(self):
        self._is_synced = False
        self._connection.close()

    def on_sync_response(self, sync_id, body: str):
        if not self._cancelled:
            if self.sync_id == sync_id:
                self._sync_response = body

    def subscribe(self, subscriber: IDistOutgoingSubscriber) -> None:
        """
        :param subscriber: Subscribes to outgoing data.
        :type subscriber: IDistOutgoingSubscriber
        """

        if subscriber not in self._subs:
            self._subs.append(subscriber)

    def unsubscribe(self, unsubscriber: IDistOutgoingSubscriber) -> None:
        """
        :param unsubscriber: Unsubscribes to outgoing data.
        :type unsubscriber: IDistOutgoingSubscriber
        """

        if not self._cancelled:
            if unsubscriber in self._subs:
                self._subs.remove(unsubscriber)

    def _sync(self) -> None:
        sync_attempt = 0

        while not self._is_synced and sync_attempt < self.max_sync_attempts:
            sync_attempt += 1
            self._is_synced = self._sync_request()

        # assume nothing to sync (i.e. no other clients) if unsuccessful in
        # all attempts
        self._is_synced = True

        for subscriber in self._subs:
            subscriber.on_sync()

    def _sync_request(self, timeout: int = 3) -> bool:
        self._sync_response = None
        self.sync_id = str(uuid4())

        self._channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=bdc.SYNC_REQ,
            properties=pika.BasicProperties(
                reply_to=bdc.SYNC_RES,
                message_id=self.user_id,
                correlation_id=self.sync_id,
            ),
            body=str())

        time_sent = time()

        # while no response and no timeout
        while self._sync_response is None and (time() - time_sent) < timeout:
            self._connection.process_data_events()

        # if timeout (i.e. no response), assume there are no other clients
        if self._sync_response is None:
            return False

        self.decider.put_current_state(json.loads(self._sync_response))

        return True

    def _send_events(self, queue: Queue, routing_key: str):
        if not queue.empty():
            data = queue.get_nowait()

            if data is not None:
                data_json = json.dumps(data)
                self._channel.basic_publish(
                    exchange=self.exchange_name,
                    properties=pika.spec.BasicProperties(
                        message_id=self.user_id),
                    routing_key=routing_key,
                    body=data_json
                )

    def on_handler_transition(self,
                              nfa_name: str,
                              run_id: str,
                              state_name_from: str,
                              state_name_to: str,
                              event: BoboEvent):
        if not self._cancelled:
            self._queue_transition.put_nowait({
                bdc.NFA_NAME: nfa_name,
                bdc.RUN_ID: run_id,
                bdc.STATE_FROM: state_name_from,
                bdc.STATE_TO: state_name_to,
                bdc.EVENT: event.to_dict()
            })

    def on_handler_clone(self,
                         nfa_name: str,
                         run_id: str,
                         state_name: str,
                         event: BoboEvent):
        if not self._cancelled:
            self._queue_clone.put_nowait({
                bdc.NFA_NAME: nfa_name,
                bdc.RUN_ID: run_id,
                bdc.STATE_TO: state_name,
                bdc.EVENT: event.to_dict()
            })

    def on_handler_halt(self,
                        nfa_name: str,
                        run_id: str):
        if not self._cancelled:
            self._queue_halt.put_nowait({
                bdc.NFA_NAME: nfa_name,
                bdc.RUN_ID: run_id
            })

    def on_handler_final(self,
                         nfa_name: str,
                         run_id: str,
                         event: CompositeEvent):
        if not self._cancelled:
            self._queue_final.put_nowait({
                bdc.NFA_NAME: nfa_name,
                bdc.RUN_ID: run_id,
                bdc.EVENT: event.to_dict()
            })

    def on_dist_run_transition(self,
                               nfa_name: str,
                               run_id: str,
                               state_name_from: str,
                               state_name_to: str,
                               event: BoboEvent):
        """"""

    def on_dist_run_clone(self,
                          nfa_name: str,
                          run_id: str,
                          next_state_name: str,
                          next_event: BoboEvent):
        """"""

    def on_dist_run_halt(self,
                         nfa_name: str,
                         run_id: str):
        """"""

    def on_dist_run_final(self,
                          nfa_name: str,
                          run_id: str,
                          event: BoboEvent) -> None:
        """"""
