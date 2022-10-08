# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from abc import abstractmethod, ABC
from typing import List

from bobocep.cep.engine.decider.bobo_decider_run import BoboDeciderRunTuple


class BoboDeciderSubscriber(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def on_decider_run_changes(
            self,
            halted_complete: List[BoboDeciderRunTuple],
            halted_incomplete: List[BoboDeciderRunTuple],
            updated: List[BoboDeciderRunTuple]):
        """"""
