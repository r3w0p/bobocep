# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from queue import Queue, Full
from threading import RLock
from typing import Tuple, Dict, List, Union

from bobocep.engine.bobo_engine_task import BoboEngineTask
from bobocep.engine.decider.bobo_decider_publisher import BoboDeciderPublisher
from bobocep.engine.decider.bobo_decider_run import BoboDeciderRun
from bobocep.engine.decider.exception.bobo_decider_queue_full_error import \
    BoboDeciderQueueFullError
from bobocep.engine.decider.exception.bobo_decider_run_not_found_error import \
    BoboDeciderRunNotFoundError
from bobocep.engine.receiver.bobo_receiver_subscriber import \
    BoboReceiverSubscriber
from bobocep.event.bobo_event import BoboEvent
from bobocep.event.bobo_history import BoboHistory
from bobocep.event.event_id.bobo_event_id import BoboEventID
from bobocep.pattern.bobo_pattern import BoboPattern


class BoboDecider(BoboEngineTask, BoboDeciderPublisher,
                  BoboReceiverSubscriber):
    _EXC_QUEUE_FULL = "queue is full (max size: {})"
    _EXC_RUN_NOT_FOUND = "run ID {} not found for pattern {}"

    def __init__(self,
                 patterns: List[BoboPattern],
                 event_id_gen: BoboEventID,
                 run_id_gen: BoboEventID,
                 max_size: int):
        super().__init__()

        self._patterns: Tuple[BoboPattern, ...] = tuple(patterns)
        self._event_id_gen = event_id_gen
        self._run_id_gen = run_id_gen
        self._runs: Dict[str, Dict[str, BoboDeciderRun]] = {}
        self._max_size = max_size
        self._history_stub = BoboHistory(events={})
        self._queue: Queue = Queue(maxsize=self._max_size)
        self._lock = RLock()

        for pattern in self._patterns:
            self._runs[pattern.name] = {}

    def update(self) -> None:
        with self._lock:
            if not self._queue.empty():
                for run in self._process_event(event=self._queue.get_nowait()):
                    for subscriber in self._subscribers:
                        subscriber.on_decider_completed_run(run=run)

    def _process_event(self, event: BoboEvent) -> List[BoboDeciderRun]:
        return self._check_against_runs(event=event) + \
               self._check_against_patterns(event=event)

    def _remove_run(self, pattern_name: str, run_id: str) -> None:
        if pattern_name in self._runs and run_id in self._runs[pattern_name]:
            del self._runs[pattern_name][run_id]
        else:
            raise BoboDeciderRunNotFoundError(
                self._EXC_RUN_NOT_FOUND.format(pattern_name, run_id))

    def _check_against_runs(self, event: BoboEvent) -> List[BoboDeciderRun]:
        completed: List[BoboDeciderRun] = []
        runs_to_remove: List[Tuple[str, str]] = []

        for pattern_name, dict_runs in self._runs.items():
            for _, run in dict_runs.items():
                if run.process(event=event):
                    if run.is_halted():
                        runs_to_remove.append((pattern_name, run.run_id))
                        if run.is_complete():
                            completed.append(run)

        for pattern_name, run_id in runs_to_remove:
            self._remove_run(pattern_name, run_id)

        return completed

    def _check_against_patterns(self,
                                event: BoboEvent) -> List[BoboDeciderRun]:
        completed = []
        for pattern in self._patterns:
            if any(predicate.evaluate(event=event, history=self._history_stub)
                   for predicate in pattern.blocks[0].predicates):
                run = BoboDeciderRun(
                    run_id=self._run_id_gen.generate(),
                    pattern=pattern,
                    event=event)
                if run.is_complete():
                    completed.append(run)
                elif not run.is_halted():
                    self._runs[pattern.name][run.run_id] = run
        return completed

    def on_receiver_event(self, event: BoboEvent):
        with self._lock:
            if not self._queue.full():
                self._queue.put(event)
            else:
                raise BoboDeciderQueueFullError(
                    self._EXC_QUEUE_FULL.format(self._max_size))

    def patterns(self) -> Tuple[BoboPattern, ...]:
        with self._lock:
            return self._patterns

    def all_runs(self) -> Tuple[BoboDeciderRun, ...]:
        with self._lock:
            runs: List[BoboDeciderRun] = []
            for pattern_name, dict_runs in self._runs.items():
                for _, run in dict_runs.items():
                    runs.append(run)
            return tuple(runs)

    def runs_from(self,
                  pattern: str) -> Tuple[BoboDeciderRun, ...]:
        with self._lock:
            if pattern in self._runs:
                return tuple(self._runs[pattern].values())
            return tuple()

    def size(self) -> int:
        with self._lock:
            return self._queue.qsize()
