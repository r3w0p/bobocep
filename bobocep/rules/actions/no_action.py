from bobocep.rules.actions.bobo_action import BoboAction
from bobocep.rules.events.composite_event import CompositeEvent


class NoAction(BoboAction):
    """
    An action that does nothing and always returns the specified boolean value.

    :param bool_return: The boolean value to always return when performing
                        the action, defaults to True.
    :type bool_return: bool, optional
    """

    def __init__(self, bool_return: bool = True) -> None:
        super().__init__()

        self._bool_return = bool_return

    def perform_action(self, event: CompositeEvent) -> bool:
        return self._bool_return
