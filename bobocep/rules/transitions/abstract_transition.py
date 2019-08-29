from abc import ABC


class AbstractTransition(ABC):
    """An abstract state transition."""

    def __init__(self) -> None:
        super().__init__()
