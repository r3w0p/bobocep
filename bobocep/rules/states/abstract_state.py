from abc import ABC


class AbstractState(ABC):
    """An abstract state for use in automata."""

    def __init__(self) -> None:
        super().__init__()
