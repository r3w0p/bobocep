from abc import abstractmethod


class BoboValidator:
    """A :code:`bobocep` data validator."""

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def validate(self, data) -> bool:
        """
        :param data: The data to validate.
        :return: True if the data is valid, False otherwise.
        """
