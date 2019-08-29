from abc import ABC


class AbstractClock(ABC):
    """An abstract clock."""

    def __init__(self) -> None:
        super().__init__()
