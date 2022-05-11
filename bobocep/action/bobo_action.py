# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC


class BoboAction(ABC):

    def __init__(self,
                 name: str):
        super().__init__()

        if len(name) == 0:
            pass  # todo raise exception

        self.name = name
