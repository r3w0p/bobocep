from abc import ABC, abstractmethod


class AbstractReceiver(ABC):
    """An abstract data receiver."""

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def add_data(self, data) -> None:
        """
        :param data: Adds new data to the receiver.
        """
