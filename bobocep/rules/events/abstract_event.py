from abc import ABC


class AbstractEvent(ABC):
    """An abstract event."""

    def __init__(self) -> None:
        super().__init__()
