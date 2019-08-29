from abc import ABC


class AbstractHistory(ABC):
    """An abstract event history."""

    def __init__(self) -> None:
        super().__init__()
