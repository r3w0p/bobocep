from typing import Set
from uuid import uuid4
from dpcontracts import require

from bobocep.pattern.bobo_pattern_layer import BoboPatternLayer
from bobocep.predicate.bobo_predicate import BoboPredicate


class BoboPatternGenerator:
    """A pattern generator.

    :param name: The name of the pattern.
    :type name: str
    """

    def __init__(self, name: str):
        super().__init__()

        self.name = name
        self.layers = []
        self.preconditions = set()
        self.haltconditions = set()

        self._started = False

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
             optional: bool = False) -> 'BoboPatternGenerator':
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

        self.layers.append(BoboPatternLayer(
            group=group,
            predicates={predicate},
            times=times,
            loop=loop,
            strict=True,
            negated=False,
            optional=optional))
        return self

    def next_any(self,
                 group: str,
                 predicates: Set[BoboPredicate],
                 times: int = 1) -> 'BoboPatternGenerator':
        # todo docstring

        self.layers.append(BoboPatternLayer(
            group=group,
            predicates=predicates,
            times=times,
            loop=False,
            strict=True,
            negated=False,
            optional=False))
        return self

    @require("'group' must be a str",
             lambda args: isinstance(args.group, str))
    @require("'predicate' must be a BoboPredicate instance",
             lambda args: isinstance(args.predicate, BoboPredicate))
    def not_next(self,
                 group: str,
                 predicate: BoboPredicate) -> 'BoboPatternGenerator':
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
                "'not_next' cannot be at the start of a pattern")

        self.layers.append(BoboPatternLayer(
            group=group,
            predicates={predicate},
            times=1,
            loop=False,
            strict=True,
            negated=True,
            optional=False))
        return self

    # todo not_next_any

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
                    optional: bool = False) -> 'BoboPatternGenerator':
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

        self.layers.append(BoboPatternLayer(
            group=group,
            predicates={predicate},
            times=times,
            loop=loop,
            strict=False,
            negated=False,
            optional=optional))
        return self

    def followed_by_any(self,
                        group: str,
                        predicates: Set[BoboPredicate],
                        times: int = 1) -> 'BoboPatternGenerator':
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

        self.layers.append(BoboPatternLayer(
            group=group,
            predicates=predicates,
            times=times,
            loop=False,
            strict=False,
            negated=False,
            optional=False))
        return self

    @require("'group' must be a str",
             lambda args: isinstance(args.group, str))
    @require("'predicate' must be a BoboPredicate instance",
             lambda args: isinstance(args.predicate, BoboPredicate))
    def not_followed_by(self,
                        group: str,
                        predicate: BoboPredicate) -> 'BoboPatternGenerator':
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
                "'not_followed_by' cannot be at the start of a pattern")

        self.layers.append(BoboPatternLayer(
            group=group,
            predicates={predicate},
            times=1,
            loop=False,
            strict=False,
            negated=True,
            optional=False))
        return self

    # todo not_followed_by_any

    @require("'group' must be a str",
             lambda args: isinstance(args.group, str))
    @require("'predicates' must be a set of BoboPredicate instances with "
             "length > 0",
             lambda args: isinstance(args.predicates, set) and
                          len(args.predicates) > 0 and
                          all(isinstance(obj, BoboPredicate) for obj in
                              args.predicates))

    @require("'predicate' must be a BoboPredicate instance",
             lambda args: isinstance(args.predicate, BoboPredicate))
    def precondition(self, predicate: BoboPredicate) -> 'BoboPatternGenerator':
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
    def haltcondition(self, predicate: BoboPredicate) -> 'BoboPatternGenerator':
        """Adds a new haltcondition predicate.

        :param predicate: The haltcondition predicate.
        :type predicate: BoboPredicate

        :return: The current pattern.
        :rtype: BoboPattern
        """

        if predicate not in self.haltconditions:
            self.haltconditions.add(predicate)

        return self
