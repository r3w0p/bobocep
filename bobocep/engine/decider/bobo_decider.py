# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from queue import Queue
from threading import RLock
from typing import Tuple, Dict, List

from bobocep.engine.bobo_engine_task import BoboEngineTask
from bobocep.engine.decider.bobo_decider_publisher import BoboDeciderPublisher
from bobocep.engine.decider.bobo_decider_run import BoboDeciderRun
from bobocep.engine.receiver.bobo_receiver_subscriber import \
    BoboReceiverSubscriber
from bobocep.event.bobo_event import BoboEvent
from bobocep.event.bobo_history import BoboHistory
from bobocep.event.event_id.bobo_event_id import BoboEventID
from bobocep.engine.decider.bobo_decider_error import \
    BoboDeciderError
from bobocep.process.bobo_process import BoboProcess


class BoboDecider(BoboEngineTask, BoboDeciderPublisher,
                  BoboReceiverSubscriber):
    _EXC_PROCESS_NAME_DUP = "duplicate name in processes: {0}"
    _EXC_QUEUE_FULL = "queue is full (max size: {0})"
    _EXC_RUN_NOT_FOUND = "run {2} not found for process {0}, pattern {1}"
    _EXC_RUN_EXISTS = "run {2} already exists for process {0}, pattern {1}"

    def __init__(self,
                 processes: List[BoboProcess],
                 event_id_gen: BoboEventID,
                 run_id_gen: BoboEventID,
                 max_size: int):
        super().__init__()

        self._processes: Dict[str, BoboProcess] = {}

        for process in processes:
            if process.name not in self._processes:
                self._processes[process.name] = process
            else:
                raise BoboDeciderError(
                    self._EXC_PROCESS_NAME_DUP.format(process.name))

        self._event_id_gen = event_id_gen
        self._run_id_gen = run_id_gen
        self._max_size = max_size
        self._runs: Dict[str, Dict[str, Dict[str, BoboDeciderRun]]] = {}
        self._history_stub = BoboHistory({})
        self._queue: Queue[BoboEvent] = Queue(self._max_size)
        self._lock = RLock()

    def update(self) -> None:
        with self._lock:
            if not self._queue.empty():
                for run in self._process_event(self._queue.get_nowait()):
                    for subscriber in self._subscribers:
                        subscriber.on_decider_completed_run(
                            process_name=run.process_name,
                            pattern_name=run.pattern.name,
                            history=run.history())

    def on_receiver_event(self, event: BoboEvent):
        with self._lock:
            if not self._queue.full():
                self._queue.put(event)
            else:
                raise BoboDeciderError(
                    self._EXC_QUEUE_FULL.format(self._max_size))

    def processes(self) -> Tuple[BoboProcess, ...]:
        with self._lock:
            return tuple(self._processes.values())

    def all_runs(self) -> Tuple[BoboDeciderRun, ...]:
        with self._lock:
            runs: List[BoboDeciderRun] = []
            for process_name, dict_patterns in self._runs.items():
                for pattern_name, dict_runs in dict_patterns.items():
                    for _, run in dict_runs.items():
                        runs.append(run)
            return tuple(runs)

    def runs_from(self,
                  process_name: str,
                  pattern_name: str) -> Tuple[BoboDeciderRun, ...]:
        with self._lock:
            if process_name in self._runs and \
                    pattern_name in self._runs[process_name]:
                return tuple(self._runs[process_name][pattern_name].values())
            return tuple()

    def size(self) -> int:
        with self._lock:
            return self._queue.qsize()

    def _process_event(self, event: BoboEvent) -> List[BoboDeciderRun]:
        return self._check_against_runs(event) + \
               self._check_against_patterns(event)

    def _check_against_runs(self, event: BoboEvent) -> List[BoboDeciderRun]:
        runs_completed: List[BoboDeciderRun] = []
        runs_to_remove: List[Tuple[str, str, str]] = []

        for process_name, dict_patterns in self._runs.items():
            for pattern_name, dict_runs in dict_patterns.items():
                for _, run in dict_runs.items():
                    if run.process(event):
                        if run.is_halted():
                            runs_to_remove.append((
                                process_name, pattern_name, run.run_id))
                            if run.is_complete():
                                runs_completed.append(run)

        for process_name, pattern_name, run_id in runs_to_remove:
            self._remove_run(process_name, pattern_name, run_id)

        return runs_completed

    def _check_against_patterns(self,
                                event: BoboEvent) -> List[BoboDeciderRun]:
        completed = []
        for process in self._processes.values():
            for pattern in process.patterns:
                if any(predicate.evaluate(event=event,
                                          history=self._history_stub)
                       for predicate in pattern.blocks[0].predicates):
                    run = BoboDeciderRun(
                        run_id=self._run_id_gen.generate(),
                        process_name=process.name,
                        pattern=pattern,
                        event=event)
                    if run.is_complete():
                        completed.append(run)
                    elif not run.is_halted():
                        self._add_run(process.name, pattern.name, run)
        return completed

    def _add_run(self,
                 process_name: str,
                 pattern_name: str,
                 run: BoboDeciderRun) -> None:
        if process_name not in self._runs:
            self._runs[process_name] = {}

        if pattern_name not in self._runs[process_name]:
            self._runs[process_name][pattern_name] = {}

        if run.run_id not in self._runs[process_name][pattern_name]:
            self._runs[process_name][pattern_name][run.run_id] = run
        else:
            pass  # todo run already exists error: _EXC_RUN_EXISTS

    def _remove_run(self,
                    process_name: str,
                    pattern_name: str,
                    run_id: str) -> None:

        if process_name in self._runs and \
                pattern_name in self._runs[process_name] and \
                run_id in self._runs[process_name][pattern_name]:
            del self._runs[process_name][pattern_name][run_id]
        else:
            raise BoboDeciderError(self._EXC_RUN_NOT_FOUND.format(
                process_name, pattern_name, run_id))
