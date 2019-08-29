from abc import ABC
from time import time_ns

from bobocep.receiver.clocks.abstract_clock import AbstractClock


class EpochNSClock(AbstractClock, ABC):
    """A clock that returns the number of nanoseconds since the epoch."""

    @staticmethod
    def generate_timestamp() -> int:
        """
        :return: Nanoseconds since the epoch.
        """
        return time_ns()
