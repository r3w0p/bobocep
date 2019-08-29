from abc import ABC


class AbstractProducer(ABC):
    """An abstract event producer."""

    def __init__(self) -> None:
        super().__init__()
