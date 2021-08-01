from dpcontracts import require, ensure

from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.bobo_history import BoboHistory
from bobocep.rules.predicates.bobo_predicate import BoboPredicate
from bobocep.rules.bobo_rule import BoboRule


class BoboState(BoboRule):
    """A state.

    :param name: The state name.
    :type name: str

    :param group: The state group for grouping multiple states.
    :type group: str

    :param predicate: The state predicate that, if True, would cause a
                      transition to this state.
    :type predicate: BoboPredicate

    :param negated: Whether the state's predicate should not happen (i.e.
                    predicate passes evaluation if False).
    :type negated: bool

    :param optional: Whether the state is optional (i.e. will not halt the
                     corresponding automaton if predicate returns False).
    :type optional: bool
    """

    @require("'name' must be a str",
             lambda args: isinstance(args.name, str))
    @require("'group' must be a str",
             lambda args: isinstance(args.group, str))
    @require("'predicate' must be an instance of BoboPredicate",
             lambda args: isinstance(args.predicate, BoboPredicate))
    @require("'negated' must be a bool",
             lambda args: isinstance(args.negated, bool))
    @require("'optional' must be a bool",
             lambda args: isinstance(args.optional, bool))
    def __init__(self,
                 name: str,
                 group: str,
                 predicate: BoboPredicate,
                 negated: bool,
                 optional: bool) -> None:
        super().__init__()

        self.name = name
        self.group = group
        self.predicate = predicate
        self.negated = negated
        self.optional = optional

    @require("'event' must be an instance of BoboEvent",
             lambda args: isinstance(args.event, BoboEvent))
    @require("'history' must be an instance of BoboHistory",
             lambda args: isinstance(args.history, BoboHistory))
    @ensure("result must be a bool",
            lambda args, result: isinstance(result, bool))
    def process(self, event: BoboEvent, history: BoboHistory) -> bool:
        """Evaluates the state predicate.

        :param event: The event to be processed.
        :type event: BoboEvent

        :param history: The events previously accepted by an earlier state.
        :type history: BoboHistory

        :return: True if the state's predicate evaluates to True,
                 False otherwise.
        :rtype: bool
        """

        return self.predicate.evaluate(event, history)
