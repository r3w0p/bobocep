from abc import ABC
from time import time_ns


class EpochNSClock(ABC):
    """A clock that returns the number of nanoseconds since the epoch."""

    @staticmethod
    def generate_timestamp() -> int:
        """
        :return: Nanoseconds since the epoch.
        """
        return time_ns()
