import json

from pika import ConnectionParameters, BlockingConnection, BasicProperties

import bobocep.setup.distributed.bobo_dist_constants as bdc
from bobocep.decider.bobo_decider import BoboDecider
from bobocep.rules.bobo_rule_builder import BoboRuleBuilder
from bobocep.setup.distributed.incoming.dist_incoming_subscriber import \
    IDistIncomingSubscriber
from bobocep.setup.distributed.outgoing.bobo_dist_outgoing import \
    BoboDistOutgoing
from bobocep.setup.task.bobo_task import BoboTask


class BoboDistIncoming(BoboTask):
    """Handles incoming synchronisation data from other :code:`bobocep`
    instances.

    :param decider: The decider to which synchronisation will occur.
    :type decider: BoboDecider

    :param exchange_name: The exchange name to connect to on the external
                          message queue system.
    :type exchange_name: str

    :param user_id: The user ID to use on the external message queue system.
    :type user_id: str

    :param parameters: Parameters to connect to a message broker.
    :type parameters: ConnectionParameters
    """

    def __init__(self,
                 outgoing: BoboDistOutgoing,
                 decider: BoboDecider,
                 exchange_name: str,
                 user_id: str,
                 parameters: ConnectionParameters) -> None:

        super().__init__()

        connection = BlockingConnection(parameters=parameters)
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
                           routing_key=bdc.ACTION)
        channel.queue_bind(exchange=exchange_name, queue=queue_name,
                           routing_key=bdc.SYNC_REQ)
        channel.queue_bind(exchange=exchange_name, queue=queue_name,
                           routing_key=bdc.SYNC_RES)

        channel.basic_consume(queue=queue_name,
                              on_message_callback=self._callback,
                              auto_ack=True)

        self.outgoing = outgoing
        self.decider = decider
        self.exchange_name = exchange_name
        self.user_id = user_id
        self.parameters = parameters

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
        if not self._is_cancelled:
            self._is_synced = True

    def subscribe(self, subscriber: IDistIncomingSubscriber) -> None:
        """
        :param subscriber: Subscribes to incoming data.
        :type subscriber: IDistIncomingSubscriber
        """
        if not self._is_cancelled:
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

        elif method.routing_key == bdc.ACTION:
            self._handle_action(body)

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

    def _handle_action(self, data: str) -> None:
        json_data = json.loads(data)
        event = BoboRuleBuilder.action(json_data[bdc.EVENT])

        for subscriber in self._subs:
            subscriber.on_dist_action(event=event)

    def _handle_sync_request(self, ch, method, properties, body):
        if properties.message_id == self.user_id:
            return

        handlers = self.decider.get_all_handlers()

        json_data = json.dumps({
            bdc.HANDLERS: [handler.to_dict() for handler in handlers]
        })

        ch.basic_publish(exchange=self.exchange_name,
                         routing_key=properties.reply_to,
                         properties=BasicProperties(
                             message_id=self.user_id,
                             correlation_id=properties.correlation_id),
                         body=json_data)

    def _handle_sync_response(self, ch, method, properties, body):
        if properties.message_id == self.user_id:
            return

        self.outgoing.on_sync_response(
            sync_id=properties.correlation_id,
            body=body)

    def _setup(self) -> None:
        """"""
