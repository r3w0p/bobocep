from abc import ABC, abstractmethod


class AbstractFormatter(ABC):
    """An abstract formatter."""

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def format(self, data):
        """
        :param data: The data to format.
        :return: The new format of the data.
        """
