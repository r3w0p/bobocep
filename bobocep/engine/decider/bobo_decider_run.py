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

            if block.loop:
                self._process_loop(event, block)
            else:
                self._process_not_loop(event, block)

    def _process_loop(self,
                      event: BoboEvent,
                      block: BoboPatternBlock) -> None:
        # a looping block can neither be negated nor optional
        match = self._is_match(event, block.predicates)

        if not match:
            if block.strict:
                self._halted = True

            elif self._block_index + 1 < len(self.pattern.blocks):
                block = self.pattern.blocks[self._block_index + 1]
                if block.loop:
                    self._process_loop(event, block)
                else:
                    self._process_not_loop(event, block)

    def _process_not_loop(self,
                          event: BoboEvent,
                          block: BoboPatternBlock) -> None:
        # a non-looping block cannot be both negated and optional
        # a strict block cannot be optional
        match = self._is_match(event, block.predicates)

        if block.negated:
            if match and block.strict:
                self._halted = True

        elif block.optional:
            if not match and self._block_index + 1 < len(self.pattern.blocks):
                block = self.pattern.blocks[self._block_index + 1]
                if block.loop:
                    self._process_loop(event, block)
                else:
                    self._process_not_loop(event, block)

        else:
            if (not match) and block.strict:
                self._halted = True

    def _is_match(self,
                  event: BoboEvent,
                  predicates: List[BoboPredicate]) -> bool:
        return any(predicate.evaluate(event=event, history=self.history)
                   for predicate in predicates)
