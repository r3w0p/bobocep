# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from bobocep.action.bobo_action import BoboAction
from bobocep.action.bobo_action_response import BoboActionResponse


class BoboActionRequest:

    def __init__(self,
                 handler_name: str,
                 action: BoboAction):
        super().__init__()

        if len(handler_name) == 0:
            pass  # todo raise exception

        self.handler_name = handler_name
        self.action = action

    def execute(self) -> BoboActionResponse:
        pass
