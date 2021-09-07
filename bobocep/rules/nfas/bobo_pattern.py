from typing import List
from dpcontracts import require
from bobocep.rules.nfas.bobo_pattern_layer import BoboPatternLayer
from bobocep.rules.predicates.bobo_predicate import BoboPredicate
from bobocep.rules.nfas.bobo_nfa import BoboNFA


class BoboPattern:
    """A pattern that describes the structure of a nondeterministic finite
    automata, where each layer consists of a group of states."""

    def __init__(self) -> None:
        super().__init__()

        self.layers = []
        self.preconditions = []
        self.haltconditions = []

        self._started = False

    def generate_nfa(self) -> BoboNFA:
        """"""  # todo

    @require("'group' must be a str",
             lambda args: isinstance(args.group, str))
    @require("'predicate' must be a BoboPredicate instance",
             lambda args: isinstance(args.predicate, BoboPredicate))
    def start(self,
              group: str,
              predicate: BoboPredicate) -> 'BoboPattern':
        """
        Adds a start state.

        :param group: The group with which the state will be associated.
        :type group: str

        :param predicate: The predicate that the state will use for evaluation.
        :type predicate: BoboPredicate

        :return: The current pattern.
        """

        self.layers.append(BoboPatternLayer(
            group=group,
            predicates=[predicate],
            times=1,
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
        """Adds a new state, with strict contiguity.

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
        """

        if not self._started:
            raise RuntimeError(
                "Method 'start' must be called before 'next'")

        self.layers.append(BoboPatternLayer(
            group=group,
            predicates=[predicate],
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
        """Adds a new negated state, with strict contiguity.

        :param group: The group with which the state will be associated.
        :type group: str

        :param predicate: The predicate that the state will use for evaluation.
        :type predicate: BoboPredicate

        :return: The current pattern.
        """

        if not self._started:
            raise RuntimeError(
                "Method 'start' must be called before 'not_next'")

        self.layers.append(BoboPatternLayer(
            group=group,
            predicates=[predicate],
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
        """Adds a new state, with relaxed contiguity.

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
        """

        if not self._started:
            raise RuntimeError(
                "Method 'start' must be called before 'followed_by'")

        self.layers.append(BoboPatternLayer(
            group=group,
            predicates=[predicate],
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
        """Adds a new negated state, with relaxed contiguity.

        :param group: The group with which the state will be associated.
        :type group: str

        :param predicate: The predicate that the state will use for evaluation.
        :type predicate: BoboPredicate

        :return: The current pattern.
        """

        if not self._started:
            raise RuntimeError(
                "Method 'start' must be called before 'not_followed_by'")

        self.layers.append(BoboPatternLayer(
            group=group,
            predicates=[predicate],
            times=1,
            loop=False,
            strict=False,
            negated=True,
            optional=False))
        return self

    @require("'group' must be a str",
             lambda args: isinstance(args.group, str))
    @require("'predicates' must be a list of BoboPredicate instances with "
             "length > 0",
             lambda args: isinstance(args.predicates, list) and
                          len(args.predicates) > 0 and
                          all(isinstance(obj, BoboPredicate) for obj in
                              args.predicates))
    def followed_by_any(self,
                        group: str,
                        predicates: List[BoboPredicate]) -> 'BoboPattern':
        """Adds a new state for each predicate, with non-deterministic relaxed
        contiguity.

        :param group: The group with which the states will be associated.
        :type group: str

        :param predicates: The predicates that the states will use for
                           evaluation.
        :type predicates: List[BoboPredicate]

        :return: The current pattern.
        """

        if not self._started:
            raise RuntimeError(
                "Method 'start' must be called before 'followed_by_any'")

        self.layers.append(BoboPatternLayer(
            group=group,
            predicates=predicates,
            times=1,
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
        """

        self.preconditions.append(predicate)
        return self

    @require("'predicate' must be a BoboPredicate instance",
             lambda args: isinstance(args.predicate, BoboPredicate))
    def haltcondition(self, predicate: BoboPredicate) -> 'BoboPattern':
        """Adds a new haltcondition predicate.

        :param predicate: The haltcondition predicate.
        :type predicate: BoboPredicate

        :return: The current pattern.
        """

        self.haltconditions.append(predicate)
        return self
