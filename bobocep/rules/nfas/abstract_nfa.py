from abc import ABC


class AbstractNFA(ABC):
    """An abstract nondeterministic finite automaton."""

    def __init__(self) -> None:
        super().__init__()
