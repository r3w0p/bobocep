from typing import Set
from uuid import uuid4
from dpcontracts import require

from bobocep.rules.nfas.bobo_nfa import BoboNFA
from bobocep.rules.nfas.bobo_pattern_layer import BoboPatternLayer
from bobocep.rules.predicates.bobo_predicate import BoboPredicate
from bobocep.rules.states.bobo_state import BoboState
from bobocep.rules.states.bobo_transition import BoboTransition
from bobocep.rules.predicates.bobo_predicate_true import BoboPredicateTrue


class BoboPattern:
    """A pattern that describes the structure of a nondeterministic finite
    automata, where each layer consists of a group of states.

    :param name: The name of the pattern.
    :type name: str
    """

    _STATE = "state"

    def __init__(self, name: str):
        super().__init__()

        self.name = name
        self.layers = []
        self.preconditions = set()
        self.haltconditions = set()

        self._started = False

    def generate_nfa(self) -> BoboNFA:
        """Generates an NFA from the pattern.

        :return: A new BoboNFA instance.
        :rtype: BoboNFA
        """

        # todo :raises RuntimeError: ...

        if len(self.layers) == 0:
            raise RuntimeError("Pattern does not contain any layers")

        nfa_name = self.name
        nfa_states = {}
        nfa_transitions = {}
        nfa_start_state_name = None
        nfa_preconditions = self.preconditions.copy()
        nfa_haltconditions = self.haltconditions.copy()

        all_state_names = set()
        all_group_names = set()
        last_states = []
        last_layer = None

        for i, layer in enumerate(self.layers):
            all_group_names.add(layer.group)

            for j in range(layer.times):
                layer_states = []

                for k, predicate in enumerate(layer.predicates):
                    state_name = BoboPattern._generate_unique_name(
                        name=nfa_name,
                        ntype=BoboPattern._STATE,
                        exempt=all_state_names)

                    all_state_names.add(state_name)
                    layer_states.append(BoboState(
                        name=state_name,
                        group=layer.group,
                        predicate=predicate,
                        negated=layer.negated,
                        optional=layer.optional))

                # first state is the start state
                if i == 0 and j == 0:
                    nfa_start_state_name = layer_states[0].name

                # add states
                for state in layer_states:
                    nfa_states[state.name] = state

                # add transitions for previous state(s)
                if len(last_states) > 0 and last_layer is not None:
                    if last_layer.loop:
                        if len(last_states) > 1:
                            raise RuntimeError(
                                "Looping layer should be deterministic, "
                                "found {0} states".format(len(last_states)))
                        layer_states.append(last_states[0])

                    # create transition and apply it to the previous state(s)
                    transition = BoboTransition(
                        state_names=set(layer_states),
                        strict=layer.strict)

                    for state in last_states:
                        nfa_transitions[state.name] = transition

                last_states = layer_states
                last_layer = layer

        if nfa_start_state_name is None:
            raise RuntimeError("Start state not specified.")

        if last_states is None:
            raise RuntimeError("No previous state(s) before final state")

        if len(last_states) > 1:
            raise RuntimeError("Only 1 final state allowed, found {0}".format(
                len(last_states)))

        return BoboNFA(
            name=nfa_name,
            states=nfa_states,
            transitions=nfa_transitions,
            start_state_name=nfa_start_state_name,
            final_state_name=last_states[0].name,
            preconditions=nfa_preconditions,
            haltconditions=nfa_haltconditions)

    @staticmethod
    def _generate_unique_name(name: str, ntype: str, exempt: Set[str]):
        unique_name = None
        while unique_name is None or unique_name in exempt:
            unique_name = "{}-{}-{}".format(name, ntype, str(uuid4()))
        return unique_name

    @require("'group' must be a str",
             lambda args: isinstance(args.group, str))
    @require("'predicate' must be a BoboPredicate instance",
             lambda args: isinstance(args.predicate, BoboPredicate))
    def start(self,
              group: str,
              predicate: BoboPredicate,
              times: int = 1) -> 'BoboPattern':
        """
        Adds a start state.

        :param group: The group with which the state will be associated.
        :type group: str

        :param predicate: The predicate that the state will use for evaluation.
        :type predicate: BoboPredicate

        :param times: How many copies of the state to have in sequence,
                      default to 1.
        :type times: int, optional

        :return: The current pattern.
        :rtype: BoboPattern
        """

        self.layers.append(BoboPatternLayer(
            group=group,
            predicates={predicate},
            times=times,
            loop=False,
            strict=False,
            negated=False,
            optional=False))

        self._started = True
        return self

    @require("'group' must be a str",
             lambda args: isinstance(args.group, str))
    @require("'predicate' must be a BoboPredicate instance",
             lambda args: isinstance(args.predicate, BoboPredicate))
    @require("'times' must be a int",
             lambda args: isinstance(args.times, int))
    @require("'loop' must be a bool",
             lambda args: isinstance(args.loop, bool))
    @require("'optional' must be a bool",
             lambda args: isinstance(args.optional, bool))
    def next(self,
             group: str,
             predicate: BoboPredicate,
             times: int = 1,
             loop: bool = False,
             optional: bool = False) -> 'BoboPattern':
        """Adds a new state, with strict contiguity. The predicate must be
        fulfilled by the next event, else halt.

        :param group: The group with which the state will be associated.
        :type group: str

        :param predicate: The predicate that the state will use for evaluation.
        :type predicate: BoboPredicate

        :param times: How many copies of the state to have in sequence,
                      default to 1.
        :type times: int, optional

        :param loop: Whether the state is self-looping, defaults to False.
        :type loop: bool, optional

        :param optional: Whether the state is optional, defaults to False.
        :type optional: bool, optional

        :return: The current pattern.
        :rtype: BoboPattern
        """

        if not self._started:
            raise RuntimeError(
                "Method 'start' must be called before 'next'")

        self.layers.append(BoboPatternLayer(
            group=group,
            predicates={predicate},
            times=times,
            loop=loop,
            strict=True,
            negated=False,
            optional=optional))
        return self

    @require("'group' must be a str",
             lambda args: isinstance(args.group, str))
    @require("'predicate' must be a BoboPredicate instance",
             lambda args: isinstance(args.predicate, BoboPredicate))
    def not_next(self,
                 group: str,
                 predicate: BoboPredicate) -> 'BoboPattern':
        """Adds a new negated state, with strict contiguity. The predicate
        must not be fulfilled by the next event, else halt.

        :param group: The group with which the state will be associated.
        :type group: str

        :param predicate: The predicate that the state will use for evaluation.
        :type predicate: BoboPredicate

        :return: The current pattern.
        :rtype: BoboPattern
        """

        if not self._started:
            raise RuntimeError(
                "Method 'start' must be called before 'not_next'")

        self.layers.append(BoboPatternLayer(
            group=group,
            predicates={predicate},
            times=1,
            loop=False,
            strict=True,
            negated=True,
            optional=False))
        return self

    @require("'group' must be a str",
             lambda args: isinstance(args.group, str))
    @require("'predicate' must be a BoboPredicate instance",
             lambda args: isinstance(args.predicate, BoboPredicate))
    @require("'times' must be a int",
             lambda args: isinstance(args.times, int))
    @require("'loop' must be a bool",
             lambda args: isinstance(args.loop, bool))
    @require("'optional' must be a bool",
             lambda args: isinstance(args.optional, bool))
    def followed_by(self,
                    group: str,
                    predicate: BoboPredicate,
                    times: int = 1,
                    loop: bool = False,
                    optional: bool = False) -> 'BoboPattern':
        """Adds a new state, with relaxed contiguity. The predicate may be
        fulfilled by any future event.

        :param group: The group with which the state will be associated.
        :type group: str

        :param predicate: The predicate that the state will use for evaluation.
        :type predicate: BoboPredicate

        :param times: How many copies of the state to have in sequence,
                      default to 1.
        :type times: int, optional

        :param loop: Whether the state is self-looping, defaults to False.
        :type loop: bool, optional

        :param optional: Whether the state is optional, defaults to False.
        :type optional: bool, optional

        :return: The current pattern.
        :rtype: BoboPattern
        """

        if not self._started:
            raise RuntimeError(
                "Method 'start' must be called before 'followed_by'")

        self.layers.append(BoboPatternLayer(
            group=group,
            predicates={predicate},
            times=times,
            loop=loop,
            strict=False,
            negated=False,
            optional=optional))
        return self

    @require("'group' must be a str",
             lambda args: isinstance(args.group, str))
    @require("'predicate' must be a BoboPredicate instance",
             lambda args: isinstance(args.predicate, BoboPredicate))
    def not_followed_by(self,
                        group: str,
                        predicate: BoboPredicate) -> 'BoboPattern':
        """Adds a new negated state, with relaxed contiguity. The predicate
        may not be fulfilled by any event until a state directly after this
        state has been fulfilled.

        :param group: The group with which the state will be associated.
        :type group: str

        :param predicate: The predicate that the state will use for evaluation.
        :type predicate: BoboPredicate

        :return: The current pattern.
        :rtype: BoboPattern
        """

        if not self._started:
            raise RuntimeError(
                "Method 'start' must be called before 'not_followed_by'")

        self.layers.append(BoboPatternLayer(
            group=group,
            predicates={predicate},
            times=1,
            loop=False,
            strict=False,
            negated=True,
            optional=False))
        return self

    @require("'group' must be a str",
             lambda args: isinstance(args.group, str))
    @require("'predicates' must be a set of BoboPredicate instances with "
             "length > 0",
             lambda args: isinstance(args.predicates, set) and
                          len(args.predicates) > 0 and
                          all(isinstance(obj, BoboPredicate) for obj in
                              args.predicates))
    def followed_by_any(self,
                        group: str,
                        predicates: Set[BoboPredicate],
                        times: int = 1) -> 'BoboPattern':
        """Adds a new state for each predicate, with non-deterministic relaxed
        contiguity.

        :param group: The group with which the states will be associated.
        :type group: str

        :param predicates: The predicates that the states will use for
                           evaluation.
        :type predicates: Set[BoboPredicate]

        :param times: How many copies of the state to have in sequence,
                      default to 1.
        :type times: int, optional

        :return: The current pattern.
        :rtype: BoboPattern
        """

        if not self._started:
            raise RuntimeError(
                "Method 'start' must be called before 'followed_by_any'")

        self.layers.append(BoboPatternLayer(
            group=group,
            predicates=predicates,
            times=times,
            loop=False,
            strict=False,
            negated=False,
            optional=False))
        return self

    @require("'predicate' must be a BoboPredicate instance",
             lambda args: isinstance(args.predicate, BoboPredicate))
    def precondition(self, predicate: BoboPredicate) -> 'BoboPattern':
        """Adds a new precondition predicate.

        :param predicate: The precondition predicate.
        :type predicate: BoboPredicate

        :return: The current pattern.
        :rtype: BoboPattern
        """

        if predicate not in self.preconditions:
            self.preconditions.add(predicate)

        return self

    @require("'predicate' must be a BoboPredicate instance",
             lambda args: isinstance(args.predicate, BoboPredicate))
    def haltcondition(self, predicate: BoboPredicate) -> 'BoboPattern':
        """Adds a new haltcondition predicate.

        :param predicate: The haltcondition predicate.
        :type predicate: BoboPredicate

        :return: The current pattern.
        :rtype: BoboPattern
        """

        if predicate not in self.haltconditions:
            self.haltconditions.add(predicate)

        return self
