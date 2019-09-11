from copy import copy
from typing import List


class BoboTransition:
    """A :code:`bobocep` state transition.

    :param state_names: The names of states to which a transition can be made,
                        defaults to an empty list.
    :type state_names: List[str], optional

    :param strict: Whether strict contiguity is expected for the transition,
                   defaults to False.
    :type strict: bool, optional

    :raises RuntimeError: Using strict contiguity when more than one state is
                          provided.
    """

    STATE_NAMES = "state_names"
    STRICT = "strict"

    def __init__(self,
                 state_names: List[str] = None,
                 strict: bool = False) -> None:
        super().__init__()

        if len(state_names) > 1 and strict:
            raise RuntimeError("Must not use strict contiguity with more than "
                               "one state, found {} states."
                               .format(len(state_names)))

        self.state_names = [] if state_names is None else state_names
        self.is_strict = strict
        self.is_deterministic = len(state_names) == 1

    def to_dict(self) -> dict:
        """
        :return: A dict representation of the object.
        """

        return {
            self.STATE_NAMES: copy(self.state_names),
            self.STRICT: self.is_strict
        }
