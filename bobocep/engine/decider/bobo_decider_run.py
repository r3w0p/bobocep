# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from threading import RLock
from typing import Tuple

from bobocep.event.bobo_event import BoboEvent
from bobocep.event.bobo_history import BoboHistory
from bobocep.pattern.bobo_pattern import BoboPattern
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
        self._events = {
            self.pattern.blocks[0].group: [event]
        }
        self._block_index = 1
        self._lock = RLock()
        self._halted = self.is_complete()

    def is_complete(self) -> bool:
        with self._lock:
            return self._block_index > len(self.pattern.blocks) - 1

    def is_halted(self) -> bool:
        with self._lock:
            return self._halted

    def halt(self) -> None:
        with self._lock:
            self._halted = True

    def process(self, event: BoboEvent) -> bool:
        with self._lock:
            if self._halted:
                return False

            temp_index = self._block_index
            block: BoboPatternBlock = self.pattern.blocks[temp_index]

            if block.loop:
                return self._process_loop(event, block, temp_index)
            else:
                return self._process_not_loop(event, block, temp_index)

    def _process_loop(self,
                      event: BoboEvent,
                      block: BoboPatternBlock,
                      temp_index: int) -> bool:
        match = self._is_match(event, block.predicates)

        if not match:
            # looping block can be neither negated nor optional
            if block.strict:
                self._halted = True
                return False
            else:
                # looping block cannot be final state
                temp_index += 1
                block = self.pattern.blocks[temp_index]
                if block.loop:
                    return self._process_loop(event, block, temp_index)
                else:
                    return self._process_not_loop(event, block, temp_index)
        else:
            self._add_event(event, block)
            return True

    def _process_not_loop(self,
                          event: BoboEvent,
                          block: BoboPatternBlock,
                          temp_index: int) -> bool:
        # non-looping block cannot be both negated and optional
        match = self._is_match(event, block.predicates)

        if block.negated:
            if match and block.strict:
                self._halted = True
                return False
            else:
                self._move_forward(event, block, temp_index)
                return True

        elif block.optional:
            # strict block cannot be optional
            if not match:
                temp_index += 1
                block = self.pattern.blocks[temp_index]
                if block.loop:
                    return self._process_loop(event, block, temp_index)
                else:
                    return self._process_not_loop(event, block, temp_index)
            else:
                self._move_forward(event, block, temp_index)
                return True

        else:
            if (not match) and block.strict:
                self._halted = True
                return False
            else:
                self._move_forward(event, block, temp_index)
                return True

    def _is_match(self,
                  event: BoboEvent,
                  predicates: Tuple[BoboPredicate, ...]) -> bool:
        return any(predicate.evaluate(event=event,
                                      history=BoboHistory(events=self._events))
                   for predicate in predicates)

    def _add_event(self, event: BoboEvent, block: BoboPatternBlock):
        if block.group not in self._events:
            self._events[block.group] = []
        self._events[block.group].append(event)

    def _move_forward(self,
                      event: BoboEvent,
                      block: BoboPatternBlock,
                      temp_index: int):
        self._add_event(event, block)
        self._block_index = temp_index + 1
        self._halted = self.is_complete()
