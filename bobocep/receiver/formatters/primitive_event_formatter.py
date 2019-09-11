from bobocep.receiver.clocks.epoch_ns_clock import EpochNSClock
from bobocep.rules.events.primitive_event import PrimitiveEvent


class PrimitiveEventFormatter:
    """An PrimitiveEvent formatter."""

    def __init__(self) -> None:
        super().__init__()

    def format(self, data) -> PrimitiveEvent:
        """
        :param data: The data to format.
        :return: A new PrimitiveEvent instance containing the data.
        """
        return PrimitiveEvent(timestamp=EpochNSClock.generate_timestamp(),
                              data=data)
