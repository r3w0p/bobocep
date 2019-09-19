from typing import List

from bobocep.rules.actions.bobo_action import BoboAction
from bobocep.rules.actions.multi.multi_action import MultiAction
from bobocep.rules.events.bobo_event import BoboEvent


class SequentialAction(MultiAction):
    """An action that enables the sequential execution of multiple actions
    within a single BoboAction instance.

    :param actions: The actions to execute, in list order.
    :type actions: List[BoboAction]

    :param name: The action name, defaults to an empty string.
    :type name: str, optional

    :param all_success: All actions must be successful to be a successful
                        execution; otherwise, the success of *at least one*
                        action would result in an overall success,
                        Defaults to True.
    :type all_success: bool, optional

    :param early_stop: Will immediately return False on the first unsuccessful
                       action and not execute any remaining actions,
                       defaults to True. Note that any uncaught exception would
                       still cause an early stop and immediate failure.
    :type early_stop: bool, optional
    """

    def __init__(self,
                 actions: List[BoboAction],
                 name: str = None,
                 all_success: bool = True,
                 early_stop: bool = True) -> None:
        super().__init__(name=name)

        self._actions = actions
        self._all_success = all_success
        self._early_stop = early_stop

    def _perform_action(self, event: BoboEvent) -> bool:
        results = []

        for action in self._actions:
            if action.execute(event).success:
                results.append(True)
            elif self._early_stop:
                return False
            else:
                results.append(False)

        return all(r is True for r in results) if self._all_success \
            else any(r is True for r in results)
