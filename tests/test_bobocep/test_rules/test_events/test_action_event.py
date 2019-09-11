import unittest
from uuid import uuid4

from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.events.action_event import ActionEvent
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory


KEY_A = "key_a"
VALUE_A = "value_a"
DATA_A = {KEY_A: VALUE_A}
NAME_A = "name_a"
NAME_B = "name_b"
EXCEPTION_A = "exception_a"
DESCRIPTION_A = "description_a"
EVENT_ID_A = "event_id_a"


def generate_composite_event(name: str) -> CompositeEvent:
    return CompositeEvent(
        timestamp=EpochNSClock.generate_timestamp(),
        name=name,
        history=BoboHistory(),
        data={})


class TestActionEvent(unittest.TestCase):

    def test_to_dict_all_arguments_provided(self):
        timestamp = EpochNSClock.generate_timestamp()
        name = NAME_A
        success = True
        for_event = generate_composite_event(NAME_B)
        exception = EXCEPTION_A
        description = DESCRIPTION_A
        data = DATA_A
        event_id = EVENT_ID_A

        event = ActionEvent(
            timestamp=timestamp,
            name=name,
            success=success,
            for_event=for_event,
            exception=exception,
            description=description,
            data=data,
            event_id=event_id
        )

        self.assertDictEqual(event.to_dict(), {
            ActionEvent.TIMESTAMP: timestamp,
            ActionEvent.NAME: name,
            ActionEvent.SUCCESS: success,
            ActionEvent.FOR_EVENT: for_event.to_dict(),
            ActionEvent.EXCEPTION: exception,
            ActionEvent.DESCRIPTION: description,
            ActionEvent.DATA: data,
            ActionEvent.EVENT_ID: event_id
        })
