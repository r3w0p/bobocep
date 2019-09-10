from abc import ABC

from bobocep.rules.actions.bobo_action import BoboAction


class MultiAction(BoboAction, ABC):
    """An abstract action that enables the execution of multiple actions
    within a single BoboAction instance.

    :param name: The action name, defaults to an empty string.
    :type name: str, optional
    """

    def __init__(self, name: str = None) -> None:
        super().__init__(name=name)
