from bobocep.rules.actions.bobo_action import BoboAction
from bobocep.rules.events.bobo_event import BoboEvent


class NoAction(BoboAction):
    """
    An action that does nothing and always returns the specified boolean value.

    :param name: The action name, defaults to an empty string.
    :type name: str, optional

    :param bool_return: The boolean value to always return when performing
                        the action, defaults to True.
    :type bool_return: bool, optional
    """

    def __init__(self, name: str = None, bool_return: bool = True) -> None:
        super().__init__(name=name)

        self._bool_return = bool_return

    def _perform_action(self, event: BoboEvent) -> bool:
        return self._bool_return
