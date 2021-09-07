from bobocep.rules.predicates.bobo_predicate_callable import \
    BoboPredicateCallable
from bobocep.rules.states.bobo_state import BoboState
from bobocep.rules.states.bobo_transition import BoboTransition


def simple_state(
        state_id: str,
        group: str = None,
        negated: bool = False,
        optional: bool = False):
    return BoboState(
        name="test_state_name_{}".format(state_id),
        group="test_state_group_{}".format(
            group if group is not None else state_id),
        predicate=BoboPredicateCallable(call=lambda e, h: True),
        negated=negated,
        optional=optional
    )


def simple_transition(state_name: str, strict: bool = False):
    return BoboTransition(
        state_names={state_name},
        strict=strict
    )
