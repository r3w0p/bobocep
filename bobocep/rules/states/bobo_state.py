from dpcontracts import require, ensure

from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.bobo_history import BoboHistory
from bobocep.rules.predicates.bobo_predicate import BoboPredicate
from bobocep.rules.bobo_rule import BoboRule


class BoboState(BoboRule):
    """A state.

    :param name: The state name.
    :type name: str

    :param label: The state label for grouping multiple states.
    :type label: str

    :param predicate: The state predicate that, if True, would cause a
                      transition to this state.
    :type predicate: BoboPredicate

    :param forbidden: Whether the state's predicate should *not* happen (i.e.
                      predicate passes evaluation if False).
    :type forbidden: bool

    :param optional: Whether the state is optional (i.e. will not halt the
                     corresponding automaton if predicate returns False).
    :type optional: bool
    """

    @require("'name' must be a str",
             lambda args: isinstance(args.name, str))
    @require("'label' must be a str",
             lambda args: isinstance(args.label, str))
    @require("'predicate' must be an instance of BoboPredicate",
             lambda args: isinstance(args.predicate, BoboPredicate))
    @require("'forbidden' must be a bool",
             lambda args: isinstance(args.forbidden, bool))
    @require("'optional' must be a bool",
             lambda args: isinstance(args.optional, bool))
    def __init__(self,
                 name: str,
                 label: str,
                 predicate: BoboPredicate,
                 forbidden: bool,
                 optional: bool) -> None:
        super().__init__()

        self.name = name
        self.label = label
        self.predicate = predicate
        self.forbidden = forbidden
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
