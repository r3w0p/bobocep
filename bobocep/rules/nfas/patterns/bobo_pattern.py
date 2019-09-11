from typing import List

from bobocep.rules.nfas.patterns.bobo_pattern_layer import BoboPatternLayer
from bobocep.rules.predicates.bobo_predicate import BoboPredicate


class BoboPattern:
    """A pattern that describes the structure of a nondeterministic finite
    automata, where each layer consists of a group of states under a common
    name."""

    def __init__(self) -> None:
        super().__init__()

        self.layers = []
        self.preconditions = []
        self.haltconditions = []

    def next(self,
             label: str,
             predicate: BoboPredicate,
             times: int = 1,
             loop: bool = False,
             optional: bool = False) -> 'BoboPattern':
        """Adds a new state, with strict contiguity.

        :param label: The label with which the state will be associated.
        :type label: str

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

        self.layers.append(BoboPatternLayer(label=label,
                                            predicates=[predicate],
                                            times=times,
                                            loop=loop,
                                            strict=True,
                                            negated=False,
                                            optional=optional))
        return self

    def not_next(self,
                 label: str,
                 predicate: BoboPredicate) -> 'BoboPattern':
        """Adds a new negated state, with strict contiguity.

        :param label: The label with which the state will be associated.
        :type label: str

        :param predicate: The predicate that the state will use for evaluation.
        :type predicate: BoboPredicate

        :return: The current pattern.
        """

        self.layers.append(BoboPatternLayer(label=label,
                                            predicates=[predicate],
                                            times=1,
                                            loop=False,
                                            strict=True,
                                            negated=True,
                                            optional=False))
        return self

    def followed_by(self,
                    label: str,
                    predicate: BoboPredicate,
                    times: int = 1,
                    loop: bool = False,
                    optional: bool = False) -> 'BoboPattern':
        """Adds a new state, with relaxed contiguity.

        :param label: The label with which the state will be associated.
        :type label: str

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

        self.layers.append(BoboPatternLayer(label=label,
                                            predicates=[predicate],
                                            times=times,
                                            loop=loop,
                                            strict=False,
                                            negated=False,
                                            optional=optional))
        return self

    def not_followed_by(self,
                        label: str,
                        predicate: BoboPredicate) -> 'BoboPattern':
        """Adds a new negated state, with relaxed contiguity.

        :param label: The label with which the state will be associated.
        :type label: str

        :param predicate: The predicate that the state will use for evaluation.
        :type predicate: BoboPredicate

        :return: The current pattern.
        """

        self.layers.append(BoboPatternLayer(label=label,
                                            predicates=[predicate],
                                            times=1,
                                            loop=False,
                                            strict=False,
                                            negated=True,
                                            optional=False))
        return self

    def followed_by_any(self,
                        label: str,
                        predicates: List[BoboPredicate]) -> 'BoboPattern':
        """Adds a new state for each predicate, with non-deterministic relaxed
        contiguity.

        :param label: The label with which the states will be associated.
        :type label: str

        :param predicates: The predicates that the states will use for
                           evaluation.
        :type predicates: List[BoboPredicate]

        :return: The current pattern.
        """

        self.layers.append(BoboPatternLayer(label=label,
                                            predicates=predicates,
                                            times=1,
                                            loop=False,
                                            strict=False,
                                            negated=False,
                                            optional=False))
        return self

    def precondition(self, predicate: BoboPredicate) -> 'BoboPattern':
        """Adds a new precondition predicate.

        :param predicate: The precondition predicate.
        :type predicate: BoboPredicate

        :return: The current pattern.
        """

        self.preconditions.append(predicate)
        return self

    def haltcondition(self, predicate: BoboPredicate) -> 'BoboPattern':
        """Adds a new haltcondition predicate.

        :param predicate: The haltcondition predicate.
        :type predicate: BoboPredicate

        :return: The current pattern.
        """

        self.haltconditions.append(predicate)
        return self

    def append(self, patterns: List['BoboPattern']) -> 'BoboPattern':
        """Appends a list of patterns to the current pattern, in list order.

        :param patterns: The patterns to append to the current pattern.
        :type patterns: List[BoboPattern]

        :return: The current pattern.
        """

        for pattern in patterns:
            self.layers.extend(pattern.layers)
            self.preconditions.extend(pattern.preconditions)
            self.haltconditions.extend(pattern.haltconditions)

        return self
