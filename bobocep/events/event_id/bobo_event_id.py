from abc import ABC, abstractmethod


class BoboEventID(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def generate(self) -> str:
        """"""
