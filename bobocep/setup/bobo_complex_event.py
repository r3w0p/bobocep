from bobocep.rules.actions.bobo_action import BoboAction
from bobocep.rules.nfas.patterns.bobo_pattern import BoboPattern


class BoboComplexEvent:
    """A complex event definition. It contains the name of a complex event,
    the pattern that, if identified, infers the existence of the complex event,
    and the actions to take if the complex event were to be identified.

    :param name: The complex event name.
    :type name: str

    :param pattern: The complex event pattern.
    :type pattern: BoboPattern

    :param action: The action to perform, defaults to no action.
    :type action: BoboAction, optional
    """

    def __init__(self,
                 name: str,
                 pattern: BoboPattern,
                 action: BoboAction = None) -> None:
        super().__init__()

        self.name = name
        self.pattern = pattern
        self.action = action
