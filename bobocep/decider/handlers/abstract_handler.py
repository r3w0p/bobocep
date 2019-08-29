from abc import ABC


class AbstractHandler(ABC):
    """An abstract automaton handler."""

    def __init__(self) -> None:
        super().__init__()
