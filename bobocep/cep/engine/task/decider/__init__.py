# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Engine task that detects patterns in data and decides whether a complex event
has manifest.
"""
from collections import deque
from queue import Queue
from threading import RLock
from typing import Tuple, Dict, List, Optional, Deque

from bobocep.cep.engine.task import BoboEngineTaskError, BoboEngineTask
from bobocep.cep.engine.task.decider.pubsub import BoboDeciderPublisher
from bobocep.cep.engine.task.decider.run import BoboRunTuple, \
    BoboRun
from bobocep.cep.engine.task.receiver.pubsub import BoboReceiverSubscriber
from bobocep.cep.event import BoboHistory, BoboEvent
from bobocep.cep.gen.event_id import BoboGenEventID
from bobocep.cep.phenomenon import BoboPhenomenon, BoboPattern
from bobocep.dist.pubsub import BoboDistributedSubscriber

_EXC_PHENOM_NAME_DUP = "duplicate name in phenomena: {}"
_EXC_QUEUE_FULL = "queue is full (max size: {})"
_EXC_RUN_NOT_FOUND = "run {} not found for phenomenon {}, pattern {}"
_EXC_RUN_EXISTS = "run {} already exists for phenomenon {}, pattern {}"


class BoboError(BoboEngineTaskError):
    """
    A decider task error.
    """


class BoboDecider(BoboEngineTask,
                  BoboDeciderPublisher,
                  BoboReceiverSubscriber,
                  BoboDistributedSubscriber):
    """
    A decider task.
    """

    def __init__(self,
                 phenomena: List[BoboPhenomenon],
                 gen_event_id: BoboGenEventID,
                 gen_run_id: BoboGenEventID,
                 max_cache: int = 0,
                 max_size: int = 0):
        super().__init__()

        self._lock: RLock = RLock()
        self._closed: bool = False

        self._phenomena: Dict[str, BoboPhenomenon] = {}

        for phenom in phenomena:
            if phenom.name not in self._phenomena:
                self._phenomena[phenom.name] = phenom
            else:
                raise BoboError(
                    _EXC_PHENOM_NAME_DUP.format(phenom.name))

        self._gen_event_id: BoboGenEventID = gen_event_id
        self._gen_run_id: BoboGenEventID = gen_run_id
        # Phenomenon Name => Pattern Name => Run ID => Run
        self._runs: Dict[str, Dict[str, Dict[str, BoboRun]]] = {}
        self._stub_history: BoboHistory = BoboHistory({})
        self._max_size: int = max(0, max_size)
        self._queue: Queue[BoboEvent] = Queue(self._max_size)

        self._caching: bool = max_cache > 0
        self._cache_completed: Optional[Deque[str]] = \
            deque(maxlen=max_cache) if self._caching else None
        self._cache_halted: Optional[Deque[str]] = \
            deque(maxlen=max_cache) if self._caching else None

    def update(self) -> bool:
        """
        Performs an update cycle of the decider that takes an event from its
        queue and checks it against phenomena and existing runs.

        :return: True if an internal state change occurred during the update;
            False otherwise.
        """
        with self._lock:
            if self._closed:
                return False

            if not self._queue.empty():
                # Process event and collect changes to decider
                rl_completed, rl_halted, rl_updated = \
                    self._process_event(self._queue.get_nowait())

                completed: List[BoboRunTuple] = \
                    [run_c.to_tuple() for run_c in rl_completed]
                halted: List[BoboRunTuple] = \
                    [run_h.to_tuple() for run_h in rl_halted]
                updated: List[BoboRunTuple] = \
                    [run_u.to_tuple() for run_u in rl_updated]

                if (
                        self._caching and
                        self._cache_completed is not None and
                        self._cache_halted is not None
                ):
                    # Cache the ID of runs that have been locally completed
                    for c in completed:
                        self._cache_completed.append(c.run_id)

                    # Cache the ID of runs that have been locally halted
                    for h in halted:
                        self._cache_halted.append(h.run_id)

                # Only notify subscribers if at least one list has values
                internal_state_change = any(len(rl) > 0 for rl in
                                            [completed, halted, updated])
                if internal_state_change:
                    self._notify_subscribers(
                        completed=completed,
                        halted=halted,
                        updated=updated)

                return internal_state_change
            return False

    def on_receiver_update(self, event: BoboEvent) -> None:
        with self._lock:
            if self._closed:
                return

            if not self._queue.full():
                self._queue.put(event)
            else:
                raise BoboError(
                    _EXC_QUEUE_FULL.format(self._max_size))

    def on_distributed_update(
            self,
            completed: List[BoboRunTuple],
            halted: List[BoboRunTuple],
            updated: List[BoboRunTuple]):

        with self._lock:
            if self._closed:
                return

            if (
                    self._caching and
                    self._cache_completed is not None and
                    self._cache_halted is not None
            ):
                # Keep completed IDs if not completed locally
                # Complete takes precedent over halt and update
                completed = [cc for cc in completed
                             if cc not in self._cache_completed]

                # Keep halted IDs if not completed and not halted locally
                # Halt takes precedent over update
                halted = [ch for ch in halted
                          if ch not in self._cache_completed and
                          ch not in self._cache_halted]

                # Keep updated IDs if not completed and not halted locally
                updated = [cu for cu in updated
                           if cu not in self._cache_completed and
                           cu not in self._cache_halted]

            # Remove runs that were completed remotely
            for rc in completed:
                self._remove_run(
                    rc.phenomenon_name,
                    rc.pattern_name,
                    rc.run_id,
                    quiet=True)

            # Remove runs that were halted remotely
            for rh in halted:
                self._remove_run(
                    rh.phenomenon_name,
                    rh.pattern_name,
                    rh.run_id,
                    quiet=True)

            # Update existing runs, or add new run that was started remotely
            update_remove_indices = []
            for i, ru in enumerate(updated):
                urun: Optional[BoboRun] = self.run_at(
                    ru.phenomenon_name,
                    ru.pattern_name,
                    ru.run_id)

                if urun is not None:
                    # Update existing run
                    # Push local run forward to index and history from remote
                    if ru.block_index > urun.block_index:
                        urun.set_block(
                            block_index=ru.block_index,
                            history=ru.history)

                else:
                    pattern: Optional[BoboPattern] = self._get_pattern(
                        ru.phenomenon_name, ru.pattern_name)

                    # Ignore if pattern does not exist - it may have been
                    # removed from the decider
                    if pattern is None:
                        update_remove_indices.append(i)
                        continue

                    # Add new run that was started remotely
                    newrun = BoboRun(
                        run_id=ru.run_id,
                        phenomenon_name=ru.phenomenon_name,
                        pattern=pattern,
                        block_index=ru.block_index,
                        history=ru.history)

                    self._add_run(ru.phenomenon_name, ru.pattern_name, newrun)

            # Remove any updates for which a pattern could not be found
            for i in sorted(update_remove_indices, reverse=True):
                del updated[i]

            # Send updates to subscribers
            self._notify_subscribers(
                completed=completed,
                halted=halted,
                updated=updated)

    def _get_pattern(self,
                     phenomenon_name: str,
                     pattern_name: str) -> Optional[BoboPattern]:
        """
        :param phenomenon_name: A phenomenon name.
        :param pattern_name: A pattern name.
        :return: A BoboPattern instance corresponding to the
            phenomenon and pattern name.
        """
        for pattern in self._phenomena[phenomenon_name].patterns:
            if pattern.name == pattern_name:
                return pattern
        return None

    def phenomena(self) -> Tuple[BoboPhenomenon, ...]:
        """
        :return: All phenomena under consideration by the decider.
        """
        with self._lock:
            return tuple(self._phenomena.values())

    def all_runs(self) -> Tuple[BoboRun, ...]:
        """
        :return: All active runs in the decider.
        """
        with self._lock:
            runs: List[BoboRun] = []
            for phenomenon_name, dict_patterns in self._runs.items():
                for pattern_name, dict_runs in dict_patterns.items():
                    for _, drun in dict_runs.items():
                        runs.append(drun)
            return tuple(runs)

    def runs_from(self,
                  phenomenon_name: str,
                  pattern_name: str) -> Tuple[BoboRun, ...]:
        """
        :param phenomenon_name: A phenomenon name.
        :param pattern_name: A pattern name.
        :return: The runs associated with the given
            phenomenon and pattern name.
        """
        with self._lock:
            if (
                    phenomenon_name in self._runs and
                    pattern_name in self._runs[phenomenon_name]
            ):
                return tuple(
                    self._runs[phenomenon_name][pattern_name].values())
            return tuple()

    def run_at(self,
               phenomenon_name: str,
               pattern_name: str,
               run_id: str) -> Optional[BoboRun]:
        """
        :param phenomenon_name: A phenomenon name.
        :param pattern_name: A pattern name.
        :param run_id: A run ID.
        :return: A run associated with the given phenomenon and pattern name;
            or None if no such run exists.
        """
        with self._lock:
            if (
                    phenomenon_name in self._runs and
                    pattern_name in self._runs[phenomenon_name] and
                    run_id in self._runs[phenomenon_name][pattern_name]
            ):
                return self._runs[phenomenon_name][pattern_name][run_id]
            return None

    def size(self) -> int:
        """
        :return: The total number of events in the decider's queue.
        """
        with self._lock:
            return self._queue.qsize()

    def close(self) -> None:
        """
        Sets the decider to close.
        """
        with self._lock:
            self._closed = True

    def is_closed(self) -> bool:
        """
        :return: True if decider is set to close; False otherwise.
        """
        with self._lock:
            return self._closed

    def _notify_subscribers(
            self,
            completed: List[BoboRunTuple],
            halted: List[BoboRunTuple],
            updated: List[BoboRunTuple]) -> None:

        for subscriber in self._subscribers:
            subscriber.on_decider_update(
                completed=completed,
                halted=halted,
                updated=updated)

    def _process_event(self, event: BoboEvent) -> \
            Tuple[List[BoboRun],
                  List[BoboRun],
                  List[BoboRun]]:
        r_halt_com, r_halt_incom, r_upd = self._check_against_runs(event)
        p_halt_com, p_upd = self._check_against_patterns(event)

        return (r_halt_com + p_halt_com), r_halt_incom, (r_upd + p_upd)

    def _check_against_runs(self, event: BoboEvent) -> \
            Tuple[List[BoboRun],
                  List[BoboRun],
                  List[BoboRun]]:
        runs_halted_complete: List[BoboRun] = []
        runs_halted_incomplete: List[BoboRun] = []
        runs_updated: List[BoboRun] = []

        runs_to_remove: List[Tuple[str, str, str]] = []

        for phenomenon_name, dict_patterns in self._runs.items():
            for pattern_name, dict_runs in dict_patterns.items():
                for _, run in dict_runs.items():
                    if run.process(event):
                        if run.is_halted():
                            runs_to_remove.append((
                                phenomenon_name, pattern_name, run.run_id))
                            if run.is_complete():
                                runs_halted_complete.append(run)
                            else:
                                runs_halted_incomplete.append(run)
                        else:
                            runs_updated.append(run)

        for phenomenon_name, pattern_name, run_id in runs_to_remove:
            self._remove_run(phenomenon_name, pattern_name, run_id)

        return runs_halted_complete, runs_halted_incomplete, runs_updated

    def _check_against_patterns(self, event: BoboEvent) -> \
            Tuple[List[BoboRun],
                  List[BoboRun]]:
        runs_halted_complete: List[BoboRun] = []
        runs_updated: List[BoboRun] = []

        for phenomenon in self._phenomena.values():
            for pattern in phenomenon.patterns:
                if any(predicate.evaluate(event=event,
                                          history=self._stub_history)
                       for predicate in pattern.blocks[0].predicates):
                    newrun = BoboRun(
                        run_id=self._gen_run_id.generate(),
                        phenomenon_name=phenomenon.name,
                        pattern=pattern,
                        block_index=1,
                        history=BoboHistory({
                            pattern.blocks[0].group: [event]
                        }))

                    if newrun.is_halted() and newrun.is_complete():
                        runs_halted_complete.append(newrun)
                    else:
                        self._add_run(phenomenon.name, pattern.name, newrun)
                        runs_updated.append(newrun)

        return runs_halted_complete, runs_updated

    def _add_run(self,
                 phenomenon_name: str,
                 pattern_name: str,
                 newrun: BoboRun) -> None:
        if phenomenon_name not in self._runs:
            self._runs[phenomenon_name] = {}

        if pattern_name not in self._runs[phenomenon_name]:
            self._runs[phenomenon_name][pattern_name] = {}

        if newrun.run_id not in self._runs[phenomenon_name][pattern_name]:
            self._runs[phenomenon_name][pattern_name][newrun.run_id] = newrun
        else:
            raise BoboError(_EXC_RUN_EXISTS.format(
                newrun.run_id, phenomenon_name, pattern_name))

    def _remove_run(self,
                    phenomenon_name: str,
                    pattern_name: str,
                    run_id: str,
                    quiet: bool = False) -> None:
        """
        :param phenomenon_name: The phenomenon name.
        :param pattern_name: The pattern name.
        :param run_id: The run ID.
        :param quiet: If True, do not raise exceptions; False to raise them.

        :raises BoboDeciderError: Run is not found.
        """

        if (
                phenomenon_name in self._runs and
                pattern_name in self._runs[phenomenon_name] and
                run_id in self._runs[phenomenon_name][pattern_name]
        ):
            del self._runs[phenomenon_name][pattern_name][run_id]
        else:
            if not quiet:
                raise BoboError(_EXC_RUN_NOT_FOUND.format(
                    run_id, phenomenon_name, pattern_name))
