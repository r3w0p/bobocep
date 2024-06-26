# Copyright (c) 2019-2024 r3w0p
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

from bobocep.cep.engine.decider.pubsub import BoboDeciderPublisher, \
    BoboDeciderSubscriber
from bobocep.cep.engine.decider.run import BoboRun
from bobocep.cep.engine.decider.runserial import BoboRunSerial
from bobocep.cep.engine.receiver.pubsub import BoboReceiverSubscriber
from bobocep.cep.engine.task import BoboEngineTaskError, BoboEngineTask
from bobocep.cep.event import BoboHistory, BoboEvent
from bobocep.cep.gen.event_id import BoboGenEventID
from bobocep.cep.phenom.pattern.pattern import BoboPattern
from bobocep.cep.phenom.phenom import BoboPhenomenon
from bobocep.dist.pubsub import BoboDistributedSubscriber

_EXC_PHENOM_NAME_DUP = "duplicate name in phenomena: {}"
_EXC_QUEUE_FULL = "queue is full (max size: {})"
_EXC_RUN_NOT_FOUND = "run {} not found for phenomenon {}, pattern {}"
_EXC_RUN_EXISTS = "run {} already exists for phenomenon {}, pattern {}"


class BoboDeciderError(BoboEngineTaskError):
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
        """
        :param phenomena: List of phenomena.
        :param gen_event_id: Event ID generator.
        :param gen_run_id: Run ID generator.
        :param max_cache: Max cache size (<=0 means no caching).
            Default: 0.
        :param max_size: Max queue size.
            Default: 0 (unbounded).
        """
        super().__init__()

        self._lock: RLock = RLock()
        self._closed: bool = False
        self._subscribers: List[BoboDeciderSubscriber] = []

        self._phenomena: Dict[str, BoboPhenomenon] = {}

        for phenom in phenomena:
            if phenom.name not in self._phenomena:
                self._phenomena[phenom.name] = phenom
            else:
                raise BoboDeciderError(
                    _EXC_PHENOM_NAME_DUP.format(phenom.name))

        self._gen_event_id: BoboGenEventID = gen_event_id
        self._gen_run_id: BoboGenEventID = gen_run_id
        # Phenomenon Name => Pattern Name => Run ID => Run
        self._runs: Dict[str, Dict[str, Dict[str, BoboRun]]] = {}
        self._stub_history: BoboHistory = BoboHistory({})
        self._max_size: int = max(0, max_size)
        self._queue: Queue[BoboEvent] = Queue(self._max_size)

        self._caching: bool = max_cache > 0
        self._cache_completed: Optional[Deque[BoboRunSerial]] = \
            deque(maxlen=max_cache) if self._caching else None
        self._cache_halted: Optional[Deque[BoboRunSerial]] = \
            deque(maxlen=max_cache) if self._caching else None

    def subscribe(self, subscriber: BoboDeciderSubscriber) -> None:
        """
        :param subscriber: Subscriber to Decider data.
        """
        with self._lock:
            if subscriber not in self._subscribers:
                self._subscribers.append(subscriber)

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

                completed: List[BoboRunSerial] = \
                    [run_c.serialize() for run_c in rl_completed]
                halted: List[BoboRunSerial] = \
                    [run_h.serialize() for run_h in rl_halted]
                updated: List[BoboRunSerial] = \
                    [run_u.serialize() for run_u in rl_updated]

                # Cache local changes
                self._maybe_cache(completed, halted)

                # Only notify subscribers if at least one list has values
                internal_state_change = any(len(rl) > 0 for rl in
                                            [completed, halted, updated])
                if internal_state_change:
                    for subscriber in self._subscribers:
                        subscriber.on_decider_update(
                            completed=completed,
                            halted=halted,
                            updated=updated,
                            local=True)

                return internal_state_change
            return False

    def snapshot(self) -> Tuple[
        List[BoboRunSerial], List[BoboRunSerial], List[BoboRunSerial]
    ]:
        """
        A snapshot of the current state of the Decider.

        :return: Tuple of cached completed, cached halted, and
            currently partially-completed runs.
            If caching is disabled, the first two lists will be empty.
        """
        with self._lock:
            if self._closed:
                return [], [], []

            if (
                    self._caching and
                    self._cache_completed is not None and
                    self._cache_halted is not None
            ):
                # Get completed from cache
                r_completed = [c for c in self._cache_completed] \
                    if self._caching else []

                # Get halted from cache
                r_halted = [h for h in self._cache_halted] \
                    if self._caching else []
            else:
                r_completed = []
                r_halted = []

            # Get updated from the current state of partially-completed runs
            r_updated = []
            for k_phenom in self._runs.keys():
                for k_pattern in self._runs[k_phenom].keys():
                    for k_id in self._runs[k_phenom][k_pattern].keys():
                        r_updated.append(
                            self._runs[k_phenom][k_pattern][k_id].serialize())

            return r_completed, r_halted, r_updated

    def _maybe_cache(
            self,
            completed: List[BoboRunSerial],
            halted: List[BoboRunSerial]) -> None:
        """
        Caches completed and halted runs, if caching is enabled.

        :param completed: Completed runs.
        :param halted: Halted runs.
        """
        if (
                self._caching and
                self._cache_completed is not None and
                self._cache_halted is not None
        ):
            # Cache runs that have been locally completed
            for c in completed:
                self._cache_completed.append(c)

            # Cache runs that have been locally halted
            for h in halted:
                self._cache_halted.append(h)

    def on_receiver_update(self, event: BoboEvent) -> None:
        """
        :param event: Event from Receiver.
        """
        with self._lock:
            if self._closed:
                return

            if not self._queue.full():
                self._queue.put(event)
            else:
                raise BoboDeciderError(
                    _EXC_QUEUE_FULL.format(self._max_size))

    def _maybe_check_against_cache(
            self,
            completed: List[BoboRunSerial],
            halted: List[BoboRunSerial],
            updated: List[BoboRunSerial]) -> Tuple[List[BoboRunSerial],
                                                   List[BoboRunSerial],
                                                   List[BoboRunSerial]]:
        """
        Compares run changes that occurred remotely with local run states.

        :param completed: Completed runs.
        :param halted: Halted runs.
        :param updated: Updated runs.

        :return: The original lists but with the following changes:
            (1) completed runs kept if they have not been complete locally;
            (2) halted runs kept if not halted locally; and
            (3) updated runs kept if not completed or halted locally.
        """
        if (
                self._caching and
                self._cache_completed is not None and
                self._cache_halted is not None
        ):
            # Keep completed IDs if not completed locally
            # Complete takes precedent over halt and update
            completed = [
                comp for comp in completed
                if (
                    not any(comp.run_id == cache_comp.run_id
                            for cache_comp in self._cache_completed)
                )]

            # Keep halted IDs if not completed and not halted locally
            # Halt takes precedent over update
            halted = [ch for ch in halted
                      if ch not in self._cache_completed and
                      ch not in self._cache_halted]

            # Keep updated IDs if not completed and not halted locally
            updated = [cu for cu in updated
                       if cu not in self._cache_completed and
                       cu not in self._cache_halted]

        return completed, halted, updated

    def on_distributed_update(
            self,
            completed: List[BoboRunSerial],
            halted: List[BoboRunSerial],
            updated: List[BoboRunSerial]) -> None:
        """
        :param completed: Completed runs.
        :param halted: Halted runs.
        :param updated: Updated runs.
        """
        with self._lock:
            if self._closed:
                return

            remove_indices_completed = []
            remove_indices_halted = []
            remove_indices_updated = []
            runlocal: Optional[BoboRun] = None  # here because of mypy...

            # Remove any invalid remote changes
            completed, halted, updated = \
                self._maybe_check_against_cache(completed, halted, updated)

            # Cache remote changes
            # Note that completed and halted may be edited during the local
            # application of remote changes. Namely, if a singleton pattern
            # has two runs with differing IDs, then the local ID will replace
            # the remote ID in completed and halted, and the local ID will be
            # sent to the subscribers instead. Local IDs will also be cached
            # along with remote ones.
            self._maybe_cache(completed, halted)

            # Remove runs that were completed or halted remotely
            for i, remlist in enumerate((completed, halted)):
                for k, runremote in enumerate(remlist):
                    pattern: Optional[BoboPattern] = self._get_pattern(
                        runremote.phenomenon_name, runremote.pattern_name)

                    # Ignore if pattern does not exist
                    if pattern is None:
                        if i == 0:
                            remove_indices_completed.append(k)
                        else:
                            remove_indices_halted.append(k)

                        continue

                    runs = self.runs_from(
                        runremote.phenomenon_name, pattern.name)

                    if pattern.singleton and len(runs) > 0:
                        # If singleton run exists, remove...
                        runlocal = runs[0]

                        self._remove_run(
                            runlocal.phenomenon_name,
                            runlocal.pattern.name,
                            runlocal.run_id,
                            quiet=True)

                        # If remote run ID differs to local,
                        # replace with local run instead
                        if runremote.run_id != runlocal.run_id:
                            runlocalserial = runlocal.serialize()
                            remlist[k] = runlocalserial

                            self._maybe_cache(
                                completed=[runlocalserial] if i == 0 else [],
                                halted=[runlocalserial] if i == 1 else [])
                    else:
                        # ...else remove run with corresponding ID
                        self._remove_run(
                            runremote.phenomenon_name,
                            runremote.pattern_name,
                            runremote.run_id,
                            quiet=True)

            # Update existing runs, or add new run that was started remotely
            for k, runremote in enumerate(updated):
                pattern = self._get_pattern(
                    runremote.phenomenon_name, runremote.pattern_name)

                # Ignore if pattern does not exist
                if pattern is None:
                    remove_indices_updated.append(k)
                    continue

                if pattern.singleton:
                    # If singleton, use active run if exists...
                    runs = self.runs_from(
                        runremote.phenomenon_name, pattern.name)
                    runlocal = runs[0] if len(runs) > 0 else None
                else:
                    # ...else use run with corresponding ID
                    runlocal = self.run_at(
                        runremote.phenomenon_name,
                        runremote.pattern_name,
                        runremote.run_id)

                if runlocal is not None:
                    # If run exists, update its internal state...
                    if runremote.block_index > runlocal.block_index:
                        runlocal.set_block(
                            block_index=runremote.block_index,
                            history=runremote.history)

                    # If singleton and run ID mismatch, replace with local
                    # run instead
                    if (
                            pattern.singleton and
                            runremote.run_id != runlocal.run_id
                    ):
                        updated[k] = runlocal.serialize()
                else:
                    # ... else add new run that was started remotely
                    new_run = BoboRun(
                        run_id=runremote.run_id,
                        phenomenon_name=runremote.phenomenon_name,
                        pattern=pattern,
                        block_index=runremote.block_index,
                        history=runremote.history)

                    self._add_run(
                        runremote.phenomenon_name,
                        runremote.pattern_name,
                        new_run)

            # Remove any updates for which a pattern could not be found
            for remlist, remind in [
                (completed, remove_indices_completed),
                (halted, remove_indices_halted),
                (updated, remove_indices_updated)
            ]:
                for i in sorted(remind, reverse=True):
                    del remlist[i]

            # Notify subscribers
            for subscriber in self._subscribers:
                subscriber.on_decider_update(
                    completed=completed,
                    halted=halted,
                    updated=updated,
                    local=False)

    def _get_pattern(self,
                     phenomenon_name: str,
                     pattern_name: str) -> Optional[BoboPattern]:
        """
        :param phenomenon_name: A phenomenon name.
        :param pattern_name: A pattern name.
        :return: A BoboPattern instance corresponding to the
            phenomenon and pattern name.
        """
        if phenomenon_name in self._phenomena:
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
        Closes the Decider.
        """
        with self._lock:
            self._closed = True

    def is_closed(self) -> bool:
        """
        :return: `True` if decider is set to close; `False` otherwise.
        """
        with self._lock:
            return self._closed

    def _process_event(self, event: BoboEvent) -> \
            Tuple[List[BoboRun], List[BoboRun], List[BoboRun]]:
        """
        :param event: An event.

        :return: Runs that had a state change due to the event.
        """
        r_halt_com, r_halt_incom, r_upd = self._check_against_runs(event)
        p_halt_com, p_upd = self._check_against_patterns(event)

        return (r_halt_com + p_halt_com), r_halt_incom, (r_upd + p_upd)

    def _check_against_runs(self, event: BoboEvent) -> \
            Tuple[List[BoboRun], List[BoboRun], List[BoboRun]]:
        """
        :param event: An event.

        :return: Runs that had a state change due to the event.
        """
        runs_halted_complete: List[BoboRun] = []
        runs_halted_incomplete: List[BoboRun] = []
        runs_updated: List[BoboRun] = []

        runs_to_remove: List[Tuple[str, str, str]] = []

        for phenomenon_name, dict_patterns in self._runs.items():
            for pattern_name, dict_runs in dict_patterns.items():
                for _, run in dict_runs.items():
                    # If an internal state change occurs in the run...
                    run_eval: bool
                    try:
                        run_eval = run.process(event)
                    except (Exception,):
                        continue

                    # ...determine if completed, halted, or updated.
                    if run_eval:
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
            Tuple[List[BoboRun], List[BoboRun]]:
        """
        :param event: An event.

        :return: Newly-created runs due to the event.
        """
        runs_halted_complete: List[BoboRun] = []
        runs_updated: List[BoboRun] = []

        for phenomenon in self._phenomena.values():
            for pattern in phenomenon.patterns:
                # If any predicate in a block evaluates to True...
                any_eval: bool = False
                for predicate in pattern.blocks[0].predicates:
                    try:
                        if predicate.evaluate(event, self._stub_history):
                            any_eval = True
                            break
                    except (Exception,):
                        pass

                # ...create a run.
                if any_eval:
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
                        runs = self.runs_from(phenomenon.name, pattern.name)

                        # If not singleton, or is and no active runs
                        if (
                                (not pattern.singleton) or
                                (pattern.singleton and len(runs) == 0)
                        ):
                            self._add_run(
                                phenomenon.name,
                                pattern.name,
                                newrun)

                            runs_updated.append(newrun)

        return runs_halted_complete, runs_updated

    def _add_run(self,
                 phenomenon_name: str,
                 pattern_name: str,
                 newrun: BoboRun) -> None:
        """
        Adds new run to Decider.

        :param phenomenon_name: Phenomenon associated with new run.
        :param pattern_name: Pattern associated with new run.
        :param newrun: Run to add.
        """
        if phenomenon_name not in self._runs:
            self._runs[phenomenon_name] = {}

        if pattern_name not in self._runs[phenomenon_name]:
            self._runs[phenomenon_name][pattern_name] = {}

        if newrun.run_id not in self._runs[phenomenon_name][pattern_name]:
            self._runs[phenomenon_name][pattern_name][newrun.run_id] = newrun
        else:
            raise BoboDeciderError(_EXC_RUN_EXISTS.format(
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
                raise BoboDeciderError(_EXC_RUN_NOT_FOUND.format(
                    run_id, phenomenon_name, pattern_name))
