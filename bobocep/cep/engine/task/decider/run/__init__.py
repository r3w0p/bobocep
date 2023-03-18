# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
A partially-completed complex event.
"""

from json import loads, dumps
from threading import RLock
from typing import Tuple, Dict, List

from bobocep import BoboError
from bobocep.cep import BoboJSONable
from bobocep.cep.event import BoboHistory, BoboEvent
from bobocep.cep.phenomenon import BoboPattern
from bobocep.cep.phenomenon.pattern import BoboPatternBlock, BoboPredicate


class BoboRunError(BoboError):
    """
    A decider run error.
    """


class BoboRunTuple(BoboJSONable):
    """
    Represents the state of a run.
    """

    RUN_ID = "run_id"
    PHENOMENON_NAME = "phenomenon_name"
    PATTERN_NAME = "pattern_name"
    BLOCK_INDEX = "block_index"
    HISTORY = "history"

    def __init__(self,
                 run_id: str,
                 phenomenon_name: str,
                 pattern_name: str,
                 block_index: int,
                 history: BoboHistory):
        super().__init__()

        self._run_id: str = run_id
        self._phenomenon_name: str = phenomenon_name
        self._pattern_name: str = pattern_name
        self._block_index: int = block_index
        self._history: BoboHistory = history

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def phenomenon_name(self) -> str:
        return self._phenomenon_name

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
            self.RUN_ID: self.run_id,
            self.PHENOMENON_NAME: self.phenomenon_name,
            self.PATTERN_NAME: self.pattern_name,
            self.BLOCK_INDEX: self.block_index,
            self.HISTORY: self.history
        }, default=lambda o: o.to_json_str())

    @staticmethod
    def from_json_str(j: str) -> 'BoboRunTuple':
        return BoboRunTuple.from_dict(loads(j))

    @staticmethod
    def from_dict(d: dict) -> 'BoboRunTuple':
        return BoboRunTuple(
            run_id=d[BoboRunTuple.RUN_ID],
            phenomenon_name=d[BoboRunTuple.PHENOMENON_NAME],
            pattern_name=d[BoboRunTuple.PATTERN_NAME],
            block_index=d[BoboRunTuple.BLOCK_INDEX],
            history=BoboHistory.from_json_str(d[BoboRunTuple.HISTORY])
        )


class BoboRun:
    """
    A run that tracks the progress of a partially completed complex event.
    """

    _EXC_RUN_ID_LEN = "run ID must have a length greater than 0"
    _EXC_PHENOM_LEN = "phenomenon name must have a length greater than 0"
    _EXC_INDEX = "block index must be greater than 1"

    def __init__(self,
                 run_id: str,
                 phenomenon_name: str,
                 pattern: BoboPattern,
                 block_index: int,
                 history: BoboHistory):
        """
        :param run_id: An ID for the run.
        :param phenomenon_name: A phenomenon name associated with the run.
        :param pattern: A pattern associated with the run.
        :param block_index: An index which indicates where in the pattern
            to start the run.
        :param history: A history of events for the run.

        :raises BoboRunError: Run ID length is equal to 0.
        :raises BoboRunError: Process name length is equal to 0.
        :raises BoboRunError: Block index is less than 1.
        :raises BoboRunError: History does not have enough events in it
            to cover all blocks up to the block index.
        """
        super().__init__()
        self._lock: RLock = RLock()

        if len(run_id) == 0:
            raise BoboRunError(self._EXC_RUN_ID_LEN)

        if len(phenomenon_name) == 0:
            raise BoboRunError(self._EXC_PHENOM_LEN)

        if block_index < 1:
            raise BoboRunError(self._EXC_INDEX.format)

        # TODO Exception to check that all of the necessary groups in the
        #  new history have at least one event each in them,
        #  up to the given block index.
        #  Do this for set_block also.

        self._run_id: str = run_id
        self._phenomenon_name: str = phenomenon_name
        self._pattern: BoboPattern = pattern
        self._block_index: int = block_index
        self._history: BoboHistory = history
        self._halted: bool = self.is_complete()

    @property
    def run_id(self) -> str:
        """
        :return: The run ID.
        """
        return self._run_id

    @property
    def phenomenon_name(self) -> str:
        """
        :return: The phenomenon name associated with the run.
        """
        return self._phenomenon_name

    @property
    def pattern(self) -> BoboPattern:
        """
        :return: The pattern associated with the run.
        """
        return self._pattern

    @property
    def block_index(self) -> int:
        """
        :return: The current block index of the run.
        """
        with self._lock:
            return self._block_index

    def set_block(self, block_index: int, history: BoboHistory) -> None:
        """
        Updates the run's block to a new index and history.

        :param block_index: The new block index.
        :param history: The new history.

        :raises: BoboRunError: New block index is less than 1.
        :raises: BoboRunError: New history does not have enough events in it
            to cover all blocks up to the new block index.
        """
        with self._lock:
            if block_index < 1:
                raise BoboRunError(self._EXC_INDEX.format)

            self._block_index = block_index
            self._history = history

    def history(self) -> BoboHistory:
        """
        :return: The run history.
        """
        with self._lock:
            return self._history

    def is_complete(self) -> bool:
        """
        :return: True if run is completed; False otherwise.
        """
        with self._lock:
            return self._block_index > len(self.pattern.blocks) - 1

    def is_halted(self) -> bool:
        """
        :return: True if run has halted; False otherwise.
        """
        with self._lock:
            return self._halted

    def to_tuple(self) -> BoboRunTuple:
        """
        :return: A BoboRunTuple representation of the run.
        """
        with self._lock:
            return BoboRunTuple(
                run_id=self.run_id,
                phenomenon_name=self.phenomenon_name,
                pattern_name=self.pattern.name,
                block_index=self._block_index,
                history=self._history)

    def halt(self) -> None:
        """
        Halts the run.
        """
        with self._lock:
            self._halted = True

    def process(self, event: BoboEvent) -> bool:
        """
        :param event: An event for the run to process.
        :return: True if the event caused a state change in the run;
            False otherwise.
        """
        # True if state change occurred; False otherwise.
        # E.g. accepted event, changed block, completed, halted.
        with self._lock:
            # Do not process if the run has already finished
            if self._halted:
                return False

            # Halt if run does not match against all preconditions
            if len(self.pattern.preconditions) > 0:
                if not all([precon.evaluate(event, self._history)
                            for precon in self.pattern.preconditions]):
                    self._halted = True
                    return True

            # Halt if run matches against any haltconditions
            if len(self.pattern.haltconditions) > 0:
                if any([haltcon.evaluate(event, self._history)
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
        return any(predicate.evaluate(event, self._history)
                   for predicate in predicates)

    def _add_event(self, event: BoboEvent, block: BoboPatternBlock):
        newevents: Dict[str, List[BoboEvent]] = self._history.events

        if block.group not in newevents:
            newevents[block.group] = []

        newevents[block.group].append(event)
        self._history = BoboHistory(events=newevents)

    def _move_forward(self,
                      event: BoboEvent,
                      block: BoboPatternBlock,
                      temp_index: int):
        self._add_event(event, block)
        self._block_index = temp_index + 1
        self._halted = self.is_complete()
