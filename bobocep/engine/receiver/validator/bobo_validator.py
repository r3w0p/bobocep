from abc import ABC, abstractmethod


class BoboValidator(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def is_valid(self, entity) -> bool:
        """"""
