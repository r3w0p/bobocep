from abc import ABC


class AbstractDecider(ABC):
    """An abstract data decider."""

    def __init__(self) -> None:
        super().__init__()
