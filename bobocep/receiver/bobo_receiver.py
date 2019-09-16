from queue import Queue

from bobocep.receiver.formatters.primitive_event_formatter import \
    PrimitiveEventFormatter
from bobocep.receiver.receiver_subscriber import IReceiverSubscriber
from bobocep.receiver.validators.bobo_validator import \
    BoboValidator
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.setup.task.bobo_task import BoboTask


class BoboReceiver(BoboTask):
    """A :code:`bobocep` data receiver.

    :param validator: The data validator.
    :type validator: BoboValidator

    :param formatter: The event formatter.
    :type formatter: PrimitiveEventFormatter

    :param max_queue_size: The maximum data queue size,
                           defaults to 0 (infinite).
    :type max_queue_size: int, optional

    :param active: Whether task should start in an active state,
                   defaults to True.
    :type active: bool, optional
    """

    def __init__(self,
                 validator: BoboValidator,
                 formatter: PrimitiveEventFormatter,
                 max_queue_size: int = 0,
                 active: bool = True) -> None:
        super().__init__(active=active)

        self._data_queue = Queue(maxsize=max_queue_size)
        self._validator = validator
        self._formatter = formatter
        self._subs = []

    def _loop(self) -> None:
        if not self._data_queue.empty():
            data = self._data_queue.get_nowait()

            if self._validator.validate(data):
                self._notify_primitive_event(
                    self._formatter.format(data))
            else:
                self._notify_invalid_data(data)

    def get_validator(self) -> BoboValidator:
        """
        :return: The validator used by the Receiver.
        """

        return self._validator

    def add_data(self, data) -> None:
        """
        Add data to the receiver.

        :param data: Data to add.
        :type data: any
        """

        if not self._is_cancelled:
            self._data_queue.put_nowait(data)

    def subscribe(self, subscriber: IReceiverSubscriber) -> None:
        """
        :param subscriber: Subscribes to events from Receiver.
        :type subscriber: IReceiverSubscriber
        """

        with self._lock:
            if not self._is_cancelled and subscriber not in self._subs:
                self._subs.append(subscriber)

    def unsubscribe(self, unsubscriber: IReceiverSubscriber) -> None:
        """
        :param unsubscriber: Unsubscribes to events from Receiver.
        :type unsubscriber: IReceiverSubscriber
        """

        with self._lock:
            if unsubscriber in self._subs:
                self._subs.remove(unsubscriber)

    def _notify_primitive_event(self, event: PrimitiveEvent) -> None:
        for subscriber in self._subs:
            subscriber.on_receiver_event(event)

    def _notify_invalid_data(self, data) -> None:
        for subscriber in self._subs:
            subscriber.on_invalid_data(data)

    def _setup(self) -> None:
        """"""

    def _cancel(self) -> None:
        """"""
