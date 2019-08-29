import unittest

from bobocep.receiver.bobo_receiver import BoboReceiver
from bobocep.receiver.formatters.primitive_event_formatter import \
    PrimitiveEventFormatter
from bobocep.receiver.receiver_subscriber import IReceiverSubscriber
from bobocep.receiver.validators.str_dict_validator import StrDictValidator
from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.primitive_event import PrimitiveEvent

KEY_VAL_1 = {"key_1": "value_1"}
KEY_VAL_2 = {"key_2": "value_2"}


class ReceiverSubscriber(IReceiverSubscriber):

    def __init__(self) -> None:
        super().__init__()

        self.events = []
        self.invalid = []

    def on_receiver_event(self, event: BoboEvent):
        self.events.append(event)

    def on_invalid_data(self, data) -> None:
        self.invalid.append(data)


class TestBoboReceiver(unittest.TestCase):

    def test_process_valid_data(self):
        rec = BoboReceiver(StrDictValidator(), PrimitiveEventFormatter())
        recsub = ReceiverSubscriber()

        rec.subscribe(recsub)

        data_list = [
            {},
            KEY_VAL_1
        ]

        rec.setup()
        for data in data_list:
            rec.add_data(data)
            rec.loop()

        self.assertEqual(len(recsub.events), 2)

        for event in recsub.events:
            self.assertIsInstance(event, PrimitiveEvent)

        self.assertEqual(recsub.events[0].data, data_list[0])
        self.assertEqual(recsub.events[1].data, data_list[1])

    def test_receiver_subscribe_unsubscribe(self):
        rec = BoboReceiver(StrDictValidator(), PrimitiveEventFormatter())
        recsub = ReceiverSubscriber()

        rec.subscribe(recsub)

        # first should be passed to subscriber
        rec.add_data(KEY_VAL_1)
        rec.setup()
        rec.loop()

        self.assertEqual(len(recsub.events), 1)
        self.assertEqual(recsub.events[0].data, KEY_VAL_1)

        rec.unsubscribe(recsub)

        # second should not be passed to former subscriber
        rec.add_data(KEY_VAL_2)
        rec.loop()

        self.assertEqual(len(recsub.events), 1)
        self.assertEqual(recsub.events[0].data, KEY_VAL_1)
