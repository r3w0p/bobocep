# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""A partially-completed complex event."""

from json import loads, dumps
from threading import RLock
from typing import Tuple, Dict, List

from bobocep.cep import BoboJSONable
from bobocep.cep.event import BoboHistory, BoboEvent
from bobocep.cep.process import BoboPattern
from bobocep.cep.process.pattern import BoboPatternBlock, BoboPredicate


class BoboDeciderRunTuple(BoboJSONable):
    """Represents the state of a run."""

    PROCESS_NAME = "process_name"
    PATTERN_NAME = "pattern_name"
    BLOCK_INDEX = "block_index"
    HISTORY = "history"

    def __init__(self,
                 process_name: str,
                 pattern_name: str,
                 block_index: int,
                 history: BoboHistory):
        super().__init__()

        self._process_name: str = process_name
        self._pattern_name: str = pattern_name
        self._block_index: int = block_index
        self._history: BoboHistory = history

    @property
    def process_name(self) -> str:
        return self._process_name

    @property
    def pattern_name(self) -> str:
        return self._pattern_name

    @property
    def block_index(self) -> int:
        return self._block_index

    @property
    def history(self) -> BoboHistory:
        return self._history

    def to_json_str(self) -> str:
        return dumps({
            self.PROCESS_NAME: self.process_name,
            self.PATTERN_NAME: self.pattern_name,
            self.BLOCK_INDEX: self.block_index,
            self.HISTORY: self.history
        }, default=lambda o: o.to_json_str())

    @staticmethod
    def from_json_str(j: str) -> 'BoboDeciderRunTuple':
        return BoboDeciderRunTuple.from_dict(loads(j))

    @staticmethod
    def from_dict(d: dict) -> 'BoboDeciderRunTuple':
        return BoboDeciderRunTuple(
            process_name=d[BoboDeciderRunTuple.PROCESS_NAME],
            pattern_name=d[BoboDeciderRunTuple.PATTERN_NAME],
            block_index=d[BoboDeciderRunTuple.BLOCK_INDEX],
            history=BoboHistory.from_json_str(d[BoboDeciderRunTuple.HISTORY])
        )


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

    def to_tuple(self) -> BoboDeciderRunTuple:
        with self._lock:
            return BoboDeciderRunTuple(
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

            # Halt if run does not match against all preconditions
            if len(self.pattern.preconditions) > 0:
                if not all([
                    precon.evaluate(event, BoboHistory(self._events))
                    for precon in self.pattern.preconditions]):
                    self._halted = True
                    return True

            # Halt if run matches against any haltconditions
            if len(self.pattern.haltconditions) > 0:
                if any([
                    haltcon.evaluate(event, BoboHistory(self._events))
                    for haltcon in self.pattern.haltconditions]):
                    self._halted = True
                    return True

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
        return any(predicate.evaluate(event, BoboHistory(self._events))
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
