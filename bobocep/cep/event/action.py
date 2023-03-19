# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from json import dumps, loads
from typing import Any

from bobocep.cep.event.event import BoboEvent, BoboEventError
from bobocep.cep.event._constants import *


class BoboEventAction(BoboEvent):
    """
    An action event.
    """

    TYPE_ACTION = "action"

    PHENOMENON_NAME = "phenomenon_name"
    PATTERN_NAME = "pattern_name"
    ACTION_NAME = "action_name"
    SUCCESS = "success"

    def __init__(self,
                 event_id,
                 timestamp: int,
                 data: Any,
                 phenomenon_name: str,
                 pattern_name: str,
                 action_name: str,
                 success: bool):
        """
        :param event_id: The event ID.
        :param timestamp: The event timestamp.
        :param data: The event data.
        :param phenomenon_name: The phenomenon name.
        :param pattern_name: The pattern name.
        :param action_name: The action name.
        :param success: `True` if the action was successful;
            `False` otherwise.

        :raises BoboEventError: If length of phenomenon name is equal to 0.
        :raises BoboEventError: If length of pattern name is equal to 0.
        :raises BoboEventError: If length of action name is equal to 0.
        """
        super().__init__(
            event_id=event_id,
            timestamp=timestamp,
            data=data)

        if len(phenomenon_name) == 0:
            raise BoboEventError(EXC_PRO_LEN)

        if len(pattern_name) == 0:
            raise BoboEventError(EXC_PAT_LEN)

        if len(action_name) == 0:
            raise BoboEventError(EXC_ACT_LEN)

        self._phenomenon_name: str = phenomenon_name
        self._pattern_name: str = pattern_name
        self._action_name: str = action_name
        self._success: bool = success

    def cast(self, dtype: type) -> 'BoboEventAction':
        return BoboEventAction(
            event_id=self._event_id,
            timestamp=self._timestamp,
            data=dtype(self._data),
            phenomenon_name=self._phenomenon_name,
            pattern_name=self._pattern_name,
            action_name=self._action_name,
            success=self._success
        )

    @property
    def phenomenon_name(self) -> str:
        """
        Get phenomenon name.
        """
        return self._phenomenon_name

    @property
    def pattern_name(self) -> str:
        """
        Get pattern name.
        """
        return self._pattern_name

    @property
    def action_name(self) -> str:
        """
        Get action name.
        """
        return self._action_name

    @property
    def success(self) -> bool:
        """
        Get success.
        """
        return self._success

    def to_json_str(self) -> str:
        return dumps({
            self.EVENT_TYPE: self.TYPE_ACTION,
            self.EVENT_ID: self.event_id,
            self.TIMESTAMP: self.timestamp,
            self.DATA: self.data,
            self.PHENOMENON_NAME: self.phenomenon_name,
            self.PATTERN_NAME: self.pattern_name,
            self.ACTION_NAME: self.action_name,
            self.SUCCESS: self.success
        }, default=lambda o: o.to_json_str())

    @staticmethod
    def from_json_str(j: str) -> 'BoboEventAction':
        return BoboEventAction.from_dict(loads(j))

    @staticmethod
    def from_dict(d: dict) -> 'BoboEventAction':
        return BoboEventAction(
            event_id=d[BoboEventAction.EVENT_ID],
            timestamp=d[BoboEventAction.TIMESTAMP],
            data=d[BoboEventAction.DATA],
            phenomenon_name=d[BoboEventAction.PHENOMENON_NAME],
            pattern_name=d[BoboEventAction.PATTERN_NAME],
            action_name=d[BoboEventAction.ACTION_NAME],
            success=d[BoboEventAction.SUCCESS]
        )

    def __str__(self) -> str:
        return self.to_json_str()
