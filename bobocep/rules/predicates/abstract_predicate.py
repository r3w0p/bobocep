from abc import ABC


class AbstractPredicate(ABC):
    """An abstract predicate."""

    def __init__(self) -> None:
        super().__init__()
