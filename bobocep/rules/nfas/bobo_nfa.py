from typing import Dict, List

from dpcontracts import require

from bobocep.rules.bobo_rule import BoboRule
from bobocep.rules.predicates.bobo_predicate import BoboPredicate
from bobocep.rules.states.bobo_state import BoboState
from bobocep.rules.states.bobo_transition import BoboTransition


def _require_valid_start_state(
        states: Dict[str, BoboState],
        transitions: Dict[str, BoboTransition],
        start_state_name: str) -> bool:

    if any([
        start_state_name not in states,
        start_state_name not in transitions,
        states[start_state_name].negated,
        states[start_state_name].optional,
        start_state_name in transitions[start_state_name].state_names,
        len(transitions[start_state_name].state_names) != 1
    ]):
        return False

    return True


def _require_valid_final_state(
        states: Dict[str, BoboState],
        transitions: Dict[str, BoboTransition],
        final_state_name: str) -> bool:

    if final_state_name not in states:
        return False

    final_state = states[final_state_name]

    if any([
        final_state_name in transitions,
        final_state.negated,
        final_state.optional
    ]):
        return False

    return True


def _require_valid_second_state(
        states: Dict[str, BoboState],
        transitions: Dict[str, BoboTransition],
        start_state_name: str,
        final_state_name: str):

    second_state_name = next(iter(transitions[start_state_name].state_names))

    if second_state_name != final_state_name:
        # for reasons unknown, this needs to be separated from any()
        if second_state_name not in states:
            return False

        if any([
            second_state_name not in transitions,
            states[second_state_name].negated,
            states[second_state_name].optional
        ]):
            return False

    return True


def _require_valid_penultimate_state(
        states: Dict[str, BoboState],
        transitions: Dict[str, BoboTransition],
        final_state_name: str):

    penultimate_states = [
        state for state in states.values()
        if (state.name in transitions and
            final_state_name in transitions[state.name].state_names)
    ]

    if len(penultimate_states) == 0:
        return False

    for state in penultimate_states:
        if any([
            state.negated,
            state.optional
        ]):
            return False

    return True


def _require_valid_path_start_to_final(
        states: Dict[str, BoboState],
        transitions: Dict[str, BoboTransition],
        start_state_name: str,
        final_state_name: str) -> bool:

    state_names = set(states.keys())
    state_names_reached = set()
    state_groups_reached = set()
    state_names_current = {start_state_name}

    while final_state_name not in state_names_reached:
        group_last = None
        states_next = None

        for state_name_current in state_names_current:

            if state_name_current not in state_names:
                # test_invalid state name
                return False

            if state_name_current in state_names_reached:
                # state has already been reached
                return False

            state_current = states[state_name_current]

            if state_name_current != state_current.name:
                # inconsistent state names
                return False

            if state_current.group in state_groups_reached \
                    and state_current.group != group_last:
                # group has already been reached
                return False

            if len(state_names_current) > 1 and (state_current.negated or
                                                 state_current.optional):
                # nondeterministic group must not contain
                # negated or optional states
                return False

            state_names_reached.add(state_current.name)
            state_groups_reached.add(state_current.group)

            if state_current.name != final_state_name:
                if state_current.name not in transitions:
                    # all states require transition (if not final)
                    return False

                transition = transitions[state_current.name]
                state_transition_names = transition.state_names.copy()
                state_transition_names.discard(state_current.name)  # self loop

                if len(state_transition_names) == 0:
                    # state only has self loop
                    return False

                if group_last is None:
                    group_last = state_current.group
                elif group_last != state_current.group:
                    # current states have inconsistent groups
                    return False

                if states_next is None:
                    states_next = state_transition_names
                elif states_next != state_transition_names:
                    # current states have inconsistent transitions
                    return False

        state_names_current = states_next if states_next is not None else set()

    return True


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
                          whereby, if any precondition returns False, the
                          automaton halts.
    :type preconditions: List[BoboPredicate]

    :param haltconditions: Predicates checked before any state's predicate
                           whereby, if any haltcondition returns True, the
                           automaton halts.
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
    @require("'start_state_name' must not be the same as 'final_state_name'",
             lambda args: args.start_state_name != args.final_state_name)
    @require("transition must exist for start state",
             lambda args: args.start_state_name in args.transitions)
    @require("transition must not exist for final state",
             lambda args: args.final_state_name not in args.transitions)
    @require("_require_valid_start_state",
             lambda args: _require_valid_start_state(
                 states=args.states,
                 transitions=args.transitions,
                 start_state_name=args.start_state_name
             ))
    @require("_require_valid_final_state",
             lambda args: _require_valid_final_state(
                 states=args.states,
                 transitions=args.transitions,
                 final_state_name=args.final_state_name
             ))
    @require("_require_valid_second_state",
             lambda args: _require_valid_second_state(
                 states=args.states,
                 transitions=args.transitions,
                 start_state_name=args.start_state_name,
                 final_state_name=args.final_state_name
             ))
    @require("_require_valid_penultimate_state",
             lambda args: _require_valid_penultimate_state(
                 states=args.states,
                 transitions=args.transitions,
                 final_state_name=args.final_state_name
             ))
    @require("valid path must exist between start state and final state",
             lambda args: _require_valid_path_start_to_final(
                 states=args.states,
                 transitions=args.transitions,
                 start_state_name=args.start_state_name,
                 final_state_name=args.final_state_name
             ))
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
