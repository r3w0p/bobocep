from typing import Dict, List

from bobocep.rules.predicates.bobo_predicate import BoboPredicate
from bobocep.rules.states.bobo_state import BoboState
from bobocep.rules.transitions.bobo_transition import BoboTransition


class BoboNFA:
    """A :code:`bobocep` nondeterministic finite automaton.

    :param name: The automaton name.
    :type name: str

    :param states: The states of the automaton.
    :type states: Dict[str, BoboState]

    :param transitions: The transitions between states.
    :type transitions: Dict[str, BoboTransition]

    :param start_state_name: The name of the start state.
    :type start_state_name: str

    :param final_state_name: The name of the final state.
    :type final_state_name: str

    :param preconditions: Predicates checked before any state's predicate
                          whereby, if *any* precondition returns False,
                          the automaton halts.
    :type preconditions: List[BoboPredicate]

    :param haltconditions: Predicates checked before any state's predicate
                           whereby, if *any* haltcondition returns True,
                           the automaton halts.
    :type haltconditions: List[BoboPredicate]
    """

    def __init__(self,
                 name: str,
                 states: Dict[str, BoboState],
                 transitions: Dict[str, BoboTransition],
                 start_state_name: str,
                 final_state_name: str,
                 preconditions: List[BoboPredicate],
                 haltconditions: List[BoboPredicate]) -> None:
        super().__init__()

        self.name = name
        self.states = states
        self.transitions = transitions
        self.start_state = states[start_state_name]
        self.final_state = states[final_state_name]
        self.preconditions = preconditions
        self.haltconditions = haltconditions

        self.start_is_final = start_state_name == final_state_name
