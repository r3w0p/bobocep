from abc import ABC, abstractmethod


class BoboNullData(ABC):
    """
    An abstract class to define periodic null data.
    """

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def get_null_data(self):
        """
        :return: The null data.
        """
