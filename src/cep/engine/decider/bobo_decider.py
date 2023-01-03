# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from queue import Queue
from threading import RLock
from typing import Tuple, Dict, List

from src.cep.engine.bobo_engine_task import BoboEngineTask
from src.cep.engine.decider.bobo_decider_error import \
    BoboDeciderError
from src.cep.engine.decider.bobo_decider_publisher import \
    BoboDeciderPublisher
from src.cep.engine.decider.bobo_decider_run import BoboDeciderRun, \
    BoboDeciderRunTuple
from src.cep.engine.receiver.bobo_receiver_subscriber import \
    BoboReceiverSubscriber
from src.cep.event.bobo_event import BoboEvent
from src.cep.event.bobo_history import BoboHistory
from src.cep.event.event_id_gen.bobo_event_id_gen import BoboEventIDGen
from src.cep.process.bobo_process import BoboProcess


class BoboDecider(BoboEngineTask,
                  BoboDeciderPublisher,
                  BoboReceiverSubscriber):
    """A decider task."""

    _EXC_PROCESS_NAME_DUP = "duplicate name in processes: {0}"
    _EXC_QUEUE_FULL = "queue is full (max size: {0})"
    _EXC_RUN_NOT_FOUND = "run {2} not found for process {0}, pattern {1}"
    _EXC_RUN_EXISTS = "run {2} already exists for process {0}, pattern {1}"

    def __init__(self,
                 processes: List[BoboProcess],
                 event_id_gen: BoboEventIDGen,
                 run_id_gen: BoboEventIDGen,
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
        self._closed = False
        self._lock: RLock = RLock()

    def update(self) -> bool:
        with self._lock:
            if self._closed:
                return False

            if not self._queue.empty():
                event: BoboEvent = self._queue.get_nowait()
                halt_com, halt_incom, upd = self._process_event(event)

                serial_halt_com: List[BoboDeciderRunTuple] = \
                    [run.to_tuple() for run in halt_com]

                serial_halt_incom: List[BoboDeciderRunTuple] = \
                    [run.to_tuple() for run in halt_incom]

                serial_upd: List[BoboDeciderRunTuple] = \
                    [run.to_tuple() for run in upd]

                for subscriber in self._subscribers:
                    subscriber.on_decider_update(
                        halted_complete=serial_halt_com,
                        halted_incomplete=serial_halt_incom,
                        updated=serial_upd)

                # pytest "return True" issue - workaround...
                return event is not None
            return False

    def close(self) -> None:
        with self._lock:
            self._closed = True

    def is_closed(self) -> bool:
        with self._lock:
            return self._closed

    def on_receiver_update(self, event: BoboEvent):
        with self._lock:
            if self._closed:
                return

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

    def _process_event(self, event: BoboEvent) -> \
            Tuple[List[BoboDeciderRun],
                  List[BoboDeciderRun],
                  List[BoboDeciderRun]]:
        r_halt_com, r_halt_incom, r_upd = self._check_against_runs(event)
        p_halt_com, p_upd = self._check_against_patterns(event)

        return (r_halt_com + p_halt_com), r_halt_incom, (r_upd + p_upd)

    def _check_against_runs(self, event: BoboEvent) -> \
            Tuple[List[BoboDeciderRun],
                  List[BoboDeciderRun],
                  List[BoboDeciderRun]]:
        runs_halted_complete: List[BoboDeciderRun] = []
        runs_halted_incomplete: List[BoboDeciderRun] = []
        runs_updated: List[BoboDeciderRun] = []

        runs_to_remove: List[Tuple[str, str, str]] = []

        for process_name, dict_patterns in self._runs.items():
            for pattern_name, dict_runs in dict_patterns.items():
                for _, run in dict_runs.items():
                    if run.process(event):
                        if run.is_halted():
                            runs_to_remove.append((
                                process_name, pattern_name, run.run_id))
                            if run.is_complete():
                                runs_halted_complete.append(run)
                            else:
                                runs_halted_incomplete.append(run)
                        else:
                            runs_updated.append(run)

        for process_name, pattern_name, run_id in runs_to_remove:
            self._remove_run(process_name, pattern_name, run_id)

        return runs_halted_complete, runs_halted_incomplete, runs_updated

    def _check_against_patterns(self, event: BoboEvent) -> \
            Tuple[List[BoboDeciderRun],
                  List[BoboDeciderRun]]:
        runs_halted_complete: List[BoboDeciderRun] = []
        runs_updated: List[BoboDeciderRun] = []

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

                    if run.is_halted() and run.is_complete():
                        runs_halted_complete.append(run)
                    else:
                        self._add_run(process.name, pattern.name, run)
                        runs_updated.append(run)

        return runs_halted_complete, runs_updated

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
            raise BoboDeciderError(self._EXC_RUN_EXISTS.format(
                process_name, pattern_name, run.run_id))

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
