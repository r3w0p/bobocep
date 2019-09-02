import json

import pika

import bobocep.setup.distributed.bobo_dist_constants as bdc
from bobocep.decider.dist_decider import DistDecider
from bobocep.rules.bobo_rule_builder import BoboRuleBuilder
from bobocep.setup.distributed.incoming.dist_incoming_subscriber import \
    IDistIncomingSubscriber
from bobocep.setup.distributed.outgoing.dist_outgoing_subscriber import \
    IDistOutgoingSubscriber
from bobocep.setup.task.bobo_task import BoboTask


class BoboDistIncoming(BoboTask,
                       IDistOutgoingSubscriber):
    """Handles incoming synchronisation data from other :code:`bobocep`
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
                 host_name: str) -> None:

        super().__init__()

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host_name))
        channel = connection.channel()

        channel.exchange_declare(exchange=exchange_name,
                                 exchange_type='direct')

        result = channel.queue_declare('', exclusive=True)
        queue_name = result.method.queue

        channel.queue_bind(exchange=exchange_name, queue=queue_name,
                           routing_key=bdc.TRANSITION)
        channel.queue_bind(exchange=exchange_name, queue=queue_name,
                           routing_key=bdc.CLONE)
        channel.queue_bind(exchange=exchange_name, queue=queue_name,
                           routing_key=bdc.HALT)
        channel.queue_bind(exchange=exchange_name, queue=queue_name,
                           routing_key=bdc.FINAL)
        channel.queue_bind(exchange=exchange_name, queue=queue_name,
                           routing_key=bdc.SYNC_REQ)
        channel.queue_bind(exchange=exchange_name, queue=queue_name,
                           routing_key=bdc.SYNC_RES)

        channel.basic_consume(queue=queue_name,
                              on_message_callback=self._callback,
                              auto_ack=True)

        self.decider = decider
        self.exchange_name = exchange_name
        self.user_id = user_id
        self.host_name = host_name

        self._subs = []
        self._connection = connection
        self._channel = channel
        self._is_synced = False

    def _loop(self) -> None:
        self._channel.start_consuming()

    def _cancel(self) -> None:
        self._is_synced = False
        self._channel.stop_consuming()
        self._connection.close()

    def on_sync(self) -> None:
        if not self._cancelled:
            self._is_synced = True

    def subscribe(self, subscriber: IDistIncomingSubscriber) -> None:
        """
        :param subscriber: Subscribes to incoming data.
        :type subscriber: IDistIncomingSubscriber
        """
        if not self._cancelled:
            if subscriber not in self._subs:
                self._subs.append(subscriber)

    def unsubscribe(self, unsubscriber: IDistIncomingSubscriber) -> None:
        """
        :param unsubscriber: Unsubscribes to incoming data.
        :type unsubscriber: IDistIncomingSubscriber
        """

        if unsubscriber in self._subs:
            self._subs.remove(unsubscriber)

    def _callback(self, ch, method, properties, body):
        if properties.message_id == self.user_id:
            return

        if method.routing_key == bdc.TRANSITION:
            self._handle_transition(body)

        elif method.routing_key == bdc.CLONE:
            self._handle_clone(body)

        elif method.routing_key == bdc.HALT:
            self._handle_halt(body)

        elif method.routing_key == bdc.FINAL:
            self._handle_final(body)

        elif method.routing_key == bdc.SYNC_REQ:
            self._handle_sync_request(ch, method, properties, body)

        elif not self._is_synced and method.routing_key == bdc.SYNC_RES:
            self._handle_sync_response(ch, method, properties, body)

    def _handle_transition(self, data: str) -> None:
        json_data = json.loads(data)
        nfa_name = json_data[bdc.NFA_NAME]
        run_id = json_data[bdc.RUN_ID]
        state_from = json_data[bdc.STATE_FROM]
        state_to = json_data[bdc.STATE_TO]
        event = BoboRuleBuilder.event(json_data[bdc.EVENT])

        for subscriber in self._subs:
            subscriber.on_dist_run_transition(
                nfa_name=nfa_name,
                run_id=run_id,
                state_name_from=state_from,
                state_name_to=state_to,
                event=event
            )

    def _handle_clone(self, data: str) -> None:
        json_data = json.loads(data)
        nfa_name = json_data[bdc.NFA_NAME]
        run_id = json_data[bdc.RUN_ID]
        state_to = json_data[bdc.STATE_TO]
        event = BoboRuleBuilder.event(json_data[bdc.EVENT])

        for subscriber in self._subs:
            subscriber.on_dist_run_clone(
                nfa_name=nfa_name,
                run_id=run_id,
                next_state_name=state_to,
                next_event=event
            )

    def _handle_halt(self, data: str) -> None:
        json_data = json.loads(data)
        nfa_name = json_data[bdc.NFA_NAME]
        run_id = json_data[bdc.RUN_ID]

        for subscriber in self._subs:
            subscriber.on_dist_run_halt(
                nfa_name=nfa_name,
                run_id=run_id
            )

    def _handle_final(self, data: str) -> None:
        json_data = json.loads(data)
        nfa_name = json_data[bdc.NFA_NAME]
        run_id = json_data[bdc.RUN_ID]
        history = BoboRuleBuilder.history(json_data[bdc.HISTORY])

        for subscriber in self._subs:
            subscriber.on_dist_run_final(
                nfa_name=nfa_name,
                run_id=run_id,
                history=history
            )

    def _handle_sync_request(self, ch, method, properties, body):
        if properties.message_id == self.user_id:
            return

        json_data = json.dumps(self.decider.get_current_state())

        ch.basic_publish(exchange=self.exchange_name,
                         routing_key=properties.reply_to,
                         properties=pika.BasicProperties(
                             message_id=self.user_id,
                             correlation_id=properties.correlation_id),
                         body=json_data)

    def _handle_sync_response(self, ch, method, properties, body):
        if properties.message_id == self.user_id:
            return

        for subscriber in self._subs:
            subscriber.on_sync_response(properties.correlation_id, body)

    def _setup(self) -> None:
        """"""
