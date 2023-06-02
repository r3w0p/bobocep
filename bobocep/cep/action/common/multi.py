# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Multi actions.
"""
from abc import ABC
from typing import Tuple, Any, List

from bobocep.cep.action import BoboAction, BoboActionError
from bobocep.cep.event import BoboEventComplex


class BoboActionMulti(BoboAction, ABC):
    """
    An abstract multi action.
    """

    def __init__(self, name: str, *args, **kwargs):
        """
        :param name: The action name.
        :param args: Action arguments.
        :param kwargs: Action keyword arguments.
        """
        super().__init__(name=name, args=args, kwargs=kwargs)


class BoboActionMultiSequential(BoboActionMulti):
    """
    An abstract sequential multi action.
    """

    def __init__(self,
                 name: str,
                 actions: List[BoboAction],
                 stop_on_fail: bool,
                 *args,
                 **kwargs):
        """
        :param name: The action name.
        :param actions: The list of actions to execute.
        :param stop_on_fail: If True, the multi-action stops processing its
            action list if its current action fails. If False, it continues
            to process its remaining actions. Note: failure of any action in
            its list will cause the multi-action's success to be False.
        :param args: Action arguments.
        :param kwargs: Action keyword arguments.
        """
        super().__init__(name=name, args=args, kwargs=kwargs)

        if len(actions) < 1:
            raise BoboActionError(
                "multi sequential action {} "
                "must contain at least 1 action"
                .format(name))

        self._actions: List[BoboAction] = actions
        self._stop_on_fail: bool = stop_on_fail

    def execute(self, event: BoboEventComplex) \
            -> Tuple[bool, List[Tuple[bool, Any]]]:
        """
        :param event: The complex event that triggered action.
        :return: Whether the action execution was successful, and
            any additional data.
        """
        success = True
        data: List[Tuple[bool, Any]] = []

        for action in self._actions:
            output: Tuple[bool, Any] = action.execute(event)
            data.append(output)

            # If action was unsuccessful
            if not output[0]:
                success = False

                if self._stop_on_fail:
                    break

        return success, data
