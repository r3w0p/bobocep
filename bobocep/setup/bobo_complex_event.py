from typing import List

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

    :param actions: The actions to perform, defaults to an empty list.
    :type actions: List[BoboAction], optional
    """

    def __init__(self,
                 name: str,
                 pattern: BoboPattern,
                 actions: List[BoboAction] = None) -> None:
        super().__init__()

        self.name = name
        self.pattern = pattern
        self.actions = actions if actions is not None else []
