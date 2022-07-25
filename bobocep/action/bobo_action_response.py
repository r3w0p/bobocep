# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.


class BoboActionResponse:

    def __init__(self,
                 action_name: str,
                 success: bool):
        super().__init__()

        self.action_name = action_name
        self.success = success
