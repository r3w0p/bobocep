from typing import List

from bobocep.rules.actions.bobo_action import BoboAction
from bobocep.rules.actions.multi.multi_action import MultiAction
from bobocep.rules.events.composite_event import CompositeEvent


class SequentialAction(MultiAction):
    """An action that enables the sequential execution of multiple actions
    within a single BoboAction instance.

    :param actions: The actions to execute, in list order.
    :type actions: List[BoboAction]

    :param all_success: All actions must be successful for perform_action to
                        return True, defaults to True.
    :type all_success: bool, optional

    :param early_stop: Will immediately return False on the first unsuccessful
                       action and not execute any remaining actions,
                       defaults to True.
    :type early_stop: bool, optional
    """

    def __init__(self,
                 actions: List[BoboAction],
                 all_success: bool = True,
                 early_stop: bool = True) -> None:
        super().__init__()

        self._actions = actions
        self._all_success = all_success
        self._early_stop = early_stop

    def perform_action(self, event: CompositeEvent) -> bool:
        results = []

        for action in self._actions:
            if action.perform_action(event):
                results.append(True)
            elif self._early_stop:
                return False
            else:
                results.append(False)

        return all(r is True for r in results) if self._all_success \
            else any(r is True for r in results)
