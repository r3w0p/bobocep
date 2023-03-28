from typing import Optional, List, Any

from bobocep.cep.engine.receiver.pubsub import BoboReceiverSubscriber
from bobocep.cep.engine.receiver.receiver import BoboReceiver
from bobocep.cep.engine.receiver.validator import BoboValidator, \
    BoboValidatorAll
from bobocep.cep.event import BoboEvent
from bobocep.cep.gen.event import BoboGenEvent, BoboGenEventNone
from bobocep.cep.gen.event_id import BoboGenEventID, BoboGenEventIDUnique
from bobocep.cep.gen.timestamp import BoboGenTimestampEpoch


class StubReceiverSubscriber(BoboReceiverSubscriber):
    def __init__(self):
        super().__init__()
        self.output: List[BoboEvent] = []

    def on_receiver_update(self, event: BoboEvent):
        self.output.append(event)


def tc_receiver_sub(
        validator: Optional[BoboValidator] = None,
        event_id_gen: Optional[BoboGenEventID] = None,
        event_gen: Optional[BoboGenEvent] = None,
        max_size: int = 255):
    receiver = BoboReceiver(
        validator=validator if validator is not None else
        BoboValidatorAll(),
        gen_event_id=event_id_gen if event_id_gen is not None else
        BoboGenEventIDUnique(),
        gen_timestamp=BoboGenTimestampEpoch(),
        gen_event=event_gen if event_gen is not None else
        BoboGenEventNone(),
        max_size=max_size)

    subscriber = StubReceiverSubscriber()
    receiver.subscribe(subscriber=subscriber)

    return receiver, subscriber


class BoboValidatorRejectAll(BoboValidator):
    """Validator that always rejects data."""

    def is_valid(self, data: Any) -> bool:
        """
        :return: Always returns `False`.
        """
        return False
