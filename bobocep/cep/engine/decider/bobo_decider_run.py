# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from threading import RLock
from typing import Tuple, Dict, List

from bobocep.cep.engine.decider.bobo_decider_run_state import \
    BoboDeciderRunState
from bobocep.cep.event.bobo_event import BoboEvent
from bobocep.cep.event.bobo_history import BoboHistory
from bobocep.cep.process.pattern.bobo_pattern import BoboPattern
from bobocep.cep.process.pattern.bobo_pattern_block import BoboPatternBlock
from bobocep.cep.process.pattern.predicate.bobo_predicate import BoboPredicate


class BoboDeciderRun:
    """A decider run that tracks the progress of a partially completed complex
    event."""

    def __init__(self,
                 run_id: str,
                 process_name: str,
                 pattern: BoboPattern,
                 event: BoboEvent):
        super().__init__()
        self._lock: RLock = RLock()

        self.run_id = run_id
        self.process_name = process_name
        self.pattern = pattern
        self._events: Dict[str, List[BoboEvent]] = {
            self.pattern.blocks[0].group: [event]
        }
        self._block_index = 1
        self._halted = self.is_complete()

    def to_tuple(self) -> BoboDeciderRunState:
        with self._lock:
            return BoboDeciderRunState(
                process_name=self.process_name,
                pattern_name=self.pattern.name,
                block_index=self._block_index,
                history=BoboHistory(self._events))

    def history(self) -> BoboHistory:
        with self._lock:
            return BoboHistory(self._events)

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
        # True if state change occurred; False otherwise.
        # E.g. accepted event, changed block, completed, halted.
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

        if match:
            self._add_event(event, block)
            return True
        else:
            # Looping block can be neither negated nor optional.
            if block.strict:
                self._halted = True
                return True
            else:
                # Looping block cannot be the final state.
                temp_index += 1
                block = self.pattern.blocks[temp_index]
                if block.loop:
                    return self._process_loop(event, block, temp_index)
                else:
                    return self._process_not_loop(event, block, temp_index)

    def _process_not_loop(self,
                          event: BoboEvent,
                          block: BoboPatternBlock,
                          temp_index: int) -> bool:
        # Non-looping block cannot be both negated and optional.
        match = self._is_match(event, block.predicates)

        if block.negated:
            if match:
                # Negated predicate happened: failure.
                if block.strict:
                    self._halted = True
                    return True
                return False
            else:
                # Negated predicate did not happen: success.
                self._move_forward(event, block, temp_index)
                return True

        elif block.optional:
            # Strict block cannot be optional.
            if match:
                # Optional block consumes event.
                self._move_forward(event, block, temp_index)
                return True
            else:
                # Try event against next block.
                temp_index += 1
                block = self.pattern.blocks[temp_index]
                if block.loop:
                    return self._process_loop(event, block, temp_index)
                else:
                    return self._process_not_loop(event, block, temp_index)
        else:
            if match:
                self._move_forward(event, block, temp_index)
                return True
            else:
                if block.strict:
                    self._halted = True
                    return True
                return False

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
