from abc import ABC


class AbstractAction(ABC):
    """An abstract action."""

    def __init__(self) -> None:
        super().__init__()
