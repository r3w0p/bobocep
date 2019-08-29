from abc import ABC


class AbstractForwarder(ABC):
    """An abstract event forwarder."""

    def __init__(self) -> None:
        super().__init__()
