# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from typing import List

from bobocep.pattern.exception.bobo_pattern_block_error import \
    BoboPatternBlockError
from bobocep.predicate.bobo_predicate import BoboPredicate


class BoboPatternBlock:
    """A pattern block.

    :param group: The group with which the block is associated.
    :type group: str

    :param predicates: The predicate(s) to use for evaluation.
    :type predicates: Tuple[BoboPredicate]

    :param strict: Whether the predicate(s) has/have strict contiguity.
    :type strict: bool

    :param loop: Whether the block loops.
    :type loop: bool

    :param negated: Whether the predicate(s) is/are negated.
    :type negated: bool

    :param optional: Whether the predicate(s) is/are optional.
    :type optional: bool
    """

    _EXC_GROUP_LEN = "'group' must have a length greater than 0"
    _EXC_PREDICATES_LEN = "'predicates' must have a length greater than 0"
    _EXC_STRICT_OPT_TRUE = "'strict' and 'optional' must not both be True"
    _EXC_NEG_OR_OPT_LOOP_TRUE = "'negated' and 'optional' must " \
                                "both be False if 'loop' is True"
    _EXC_NEG_AND_OPT_LOOP_FALSE = "'negated' and 'optional' must not " \
                                  "both be True if 'loop' is False"

    def __init__(self,
                 group: str,
                 predicates: List[BoboPredicate],
                 strict: bool,
                 loop: bool,
                 negated: bool,
                 optional: bool):
        super().__init__()

        if len(group) == 0:
            raise BoboPatternBlockError(self._EXC_GROUP_LEN)

        if len(predicates) == 0:
            raise BoboPatternBlockError(self._EXC_PREDICATES_LEN)

        if strict and optional:
            raise BoboPatternBlockError(self._EXC_STRICT_OPT_TRUE)

        if loop and (negated or optional):
            raise BoboPatternBlockError(self._EXC_NEG_OR_OPT_LOOP_TRUE)

        if (not loop) and (negated and optional):
            raise BoboPatternBlockError(self._EXC_NEG_AND_OPT_LOOP_FALSE)

        self.group = group
        self.predicates = tuple(predicates)
        self.strict = strict
        self.loop = loop
        self.negated = negated
        self.optional = optional
