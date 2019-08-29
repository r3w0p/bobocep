from abc import ABC


class AbstractRun(ABC):
    """An abstract automaton run."""

    def __init__(self) -> None:
        super().__init__()
