from typing import List

from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.predicates.bobo_predicate import BoboPredicate


class BoboState:
    """A :code:`bobocep` state.

    :param name: The state name.
    :type name: str

    :param label: The state label for grouping multiple states.
    :type label: str

    :param predicate: The state predicate that, if True, would cause a
                      transition to this state.
    :type predicate: BoboPredicate

    :param negated: Whether the state's predicate should *not* happen
                    (i.e. predicate passes evaluation if False),
                    defaults to False.
    :type negated: bool, optional

    :param optional: Whether the state is optional
                     (i.e. will not halt the corresponding automaton
                     if predicate returns False)
                     defaults to False.
    :type optional: bool, optional
    """

    def __init__(self,
                 name: str,
                 label: str,
                 predicate: BoboPredicate,
                 negated: bool = False,
                 optional: bool = False) -> None:
        super().__init__()

        self.name = name
        self.label = label
        self.predicate = predicate
        self.is_negated = negated
        self.is_optional = optional

    def process(self,
                event: BoboEvent,
                history: BoboHistory,
                recent: List[BoboEvent]) -> bool:
        """Evaluates the state predicate.

        :param event: The event used in the evaluation.
        :type event: BoboEvent

        :param history: The events previously accepted by earlier the state's
                        corresponding automaton.
        :type history: BoboHistory

        :param recent: Recently accepted complex events of the corresponding
                        automaton.
        :type recent: List[BoboEvent]

        :return: True if the state's predicate evaluates to True,
                 False otherwise.
        :rtype: bool
        """

        return self.predicate.evaluate(event, history, recent)
