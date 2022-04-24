# Copyright (c) The BoboCEP Authors
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from bobocep.events.bobo_event import BoboEvent
from bobocep.events.bobo_history import BoboHistory
from bobocep.pattern.bobo_pattern import BoboPattern
from threading import RLock
from typing import List

from bobocep.pattern.bobo_pattern_block import BoboPatternBlock
from bobocep.predicate.bobo_predicate import BoboPredicate


class BoboDeciderRun:

    def __init__(self,
                 run_id: str,
                 pattern: BoboPattern,
                 event: BoboEvent):
        super().__init__()
        self.run_id = run_id
        self.pattern = pattern
        self.history = BoboHistory(events={
            self.pattern.blocks[0].group: [event]
        })
        self._block_index = 1
        self._halted = False
        self._lock = RLock()

    def is_complete(self) -> bool:
        with self._lock:
            return self._block_index > len(self.pattern.blocks) - 1

    def is_halted(self) -> bool:
        with self._lock:
            return self._halted

    def process(self, event: BoboEvent) -> bool:
        with self._lock:
            if self._halted or self.is_complete():
                return False

            block: BoboPatternBlock = self.pattern.blocks[self._block_index]
            match = self._is_match(event, block.predicates)

            # 'negated' and 'optional' must both be False if 'loop' is True
            # 'negated' and 'optional' must not both be True if 'loop' is False
            # _process_loop
            # _process_non_loop

    def _is_match(self, event: BoboEvent, predicates: List[BoboPredicate]):
        return any(predicate.evaluate(event=event, history=self.history)
                   for predicate in predicates)
