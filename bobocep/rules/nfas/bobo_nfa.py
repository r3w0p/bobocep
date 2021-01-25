from typing import Dict, List
from dpcontracts import require

from bobocep.rules.bobo_rule import BoboRule
from bobocep.rules.predicates.bobo_predicate import BoboPredicate
from bobocep.rules.states.bobo_state import BoboState
from bobocep.rules.states.bobo_transition import BoboTransition


class BoboNFA(BoboRule):
    """A nondeterministic finite automaton.

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

    @require("'name' must be a str",
             lambda args: isinstance(args.name, str))
    @require("'states' must be a dict where all keys are str and all values "
             "are BoboState instances",
             lambda args: isinstance(args.states, dict) and
                          all(isinstance(key, str) for key in
                              args.states.keys()) and
                          all(isinstance(value, BoboState) for value in
                              args.states.values()))
    @require("'transitions' must be a dict where all keys are str and all "
             "values are BoboTransition instances",
             lambda args: isinstance(args.transitions, dict) and
                          all(isinstance(key, str) for key in
                              args.transitions.keys()) and
                          all(isinstance(value, BoboTransition) for value in
                              args.transitions.values()))
    @require("'start_state_name' must be a str",
             lambda args: isinstance(args.start_state_name, str))
    @require("'final_state_name' must be a str",
             lambda args: isinstance(args.final_state_name, str))
    @require("'preconditions' must be a list of only BoboPredicate instances",
             lambda args: isinstance(args.preconditions, list) and
                          all(isinstance(pre, BoboPredicate) for pre in
                              args.preconditions))
    @require("'haltconditions' must be a list of only BoboPredicate instances",
             lambda args: isinstance(args.haltconditions, list) and
                          all(isinstance(halt, BoboPredicate) for halt in
                              args.haltconditions))
    @require("'start_state_name' must be a key in 'states'",
             lambda args: args.start_state_name in args.states)
    @require("'final_state_name' must be a key in 'states'",
             lambda args: args.final_state_name in args.states)
    # todo check states each have a transition except for final state
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
