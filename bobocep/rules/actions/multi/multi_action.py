from abc import ABC

from bobocep.rules.actions.bobo_action import BoboAction


class MultiAction(BoboAction, ABC):
    """An abstract action that enables the execution of multiple actions
    within a single BoboAction instance."""

    def __init__(self) -> None:
        super().__init__()
