from abc import ABC, abstractmethod


class BoboEngineTask(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def update(self) -> None:
        """"""
