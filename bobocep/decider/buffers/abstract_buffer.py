from abc import ABC


class AbstractBuffer(ABC):
    """An abstract data buffer."""

    def __init__(self) -> None:
        super().__init__()
