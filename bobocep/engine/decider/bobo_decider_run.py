# Copyright (c) The BoboCEP Authors
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License v3.0.

from bobocep.events.bobo_event import BoboEvent
from bobocep.events.bobo_history import BoboHistory
from bobocep.pattern.bobo_pattern import BoboPattern


class BoboDeciderRun:

    def __init__(self,
                 pattern: BoboPattern,
                 event: BoboEvent):
        super().__init__()

        self.pattern = pattern
        self.history = BoboHistory(events={
            self.pattern.blocks[0].group: [event]
        })
        self._block_index = 1

    def process(self, event: BoboEvent) -> bool:
        pass  # todo

    def is_complete(self) -> bool:
        return self._block_index > len(self.pattern.blocks)
