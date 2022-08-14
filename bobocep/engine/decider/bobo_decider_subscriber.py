# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from abc import abstractmethod, ABC

from bobocep.event.bobo_history import BoboHistory


class BoboDeciderSubscriber(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def on_decider_completed_run(self,
                                 process_name: str,
                                 pattern_name: str,
                                 history: BoboHistory):
        """"""
