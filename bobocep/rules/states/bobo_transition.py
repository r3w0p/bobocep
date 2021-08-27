from copy import copy
from typing import Set
from dpcontracts import require
from bobocep.bobo_serializable import BoboSerializable
from bobocep.rules.bobo_rule import BoboRule
from overrides import overrides


class BoboTransition(BoboSerializable, BoboRule):
    """A state transition.

    :param state_names: The names of states to which a transition can be made.
    :type state_names: Set[str]

    :param strict: Whether strict contiguity is expected for the transition.
    :type strict: bool
    """

    STATE_NAMES = "state_names"
    STRICT = "strict"

    @require("'state_names' must have a length greater than 0",
             lambda args: len(args.state_names) > 0)
    @require("'state_names' must be a set containing only type str elements",
             lambda args: isinstance(args.state_names, set) and
                          all(isinstance(name, str) for name in
                              args.state_names))
    @require("'strict' must be a bool",
             lambda args: isinstance(args.strict, bool))
    @require("'strict' must not be True when more than one state names are "
             "provided",
             lambda args: not (args.strict and len(args.state_names) > 1))
    def __init__(self,
                 state_names: Set[str],
                 strict: bool) -> None:
        super().__init__()

        self.state_names = state_names
        self.strict = strict
        self.deterministic = len(state_names) == 1
