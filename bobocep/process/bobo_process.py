# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from typing import Callable, List

from bobocep.pattern.bobo_pattern import BoboPattern


class BoboProcess:
    """A process."""

    # todo actions
    def __init__(self,
                 name: str,
                 datagen: Callable,
                 patterns: List[BoboPattern]):
        super().__init__()

        self.name = name
        self.datagen = datagen
        self.patterns = patterns
