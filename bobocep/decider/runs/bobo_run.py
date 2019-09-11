from copy import copy
from threading import RLock
from typing import List

from bobocep.decider.buffers.shared_versioned_match_buffer import \
    SharedVersionedMatchBuffer
from bobocep.decider.runs.run_subscriber import IRunSubscriber
from bobocep.decider.versions.run_version import RunVersion
from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.nfas.bobo_nfa import BoboNFA
from bobocep.rules.states.bobo_state import BoboState


class BoboRun:
    """A :code:`bobocep` antomaton run.

    :param buffer: The buffer in which run data will be stored..
    :type buffer: SharedVersionedMatchBuffer

    :param nfa: The automaton with which the run is associated.
    :type nfa: BoboNFA

    :param event: The run event.
    :type event: BoboEvent

    :param start_time: The time when the run was created. It is used for
                       generating the run ID. Defaults to the event
                       instance's timestamp.
    :type start_time: int, optional

    :param start_state: The start state of the run, defaults to the NFA's start
                        state.
    :type start_state: BoboState, optional

    :param current_state: The current state of the run, defaults to the NFA's
                          start state.
    :type current_state: BoboState, optional

    :param parent_run: The run which is this run's parent. It is used when a
                       run has been created as a consequence of non-determinism
                       (i.e. run cloning). Defaults to None.
    :type parent_run: BoboRun, optional

    :param run_id: The ID of the run. Defaults to a run ID consisting of the
                   NFA name and start time.
    :type run_id: str, optional

    :param version: The run version. If a parent run is provided, the version
                    is generated relative to the parent version.
                    Defaults to the run ID.
    :type version: RunVersion, optional

    :param put_event: Puts the run event into the buffer on instantiation,
                      defaults to True.
    :type put_event: bool, optional

    :param last_process_cloned: The last time the run processed an event,
                                a clone occurred, defaults to False.
    :type last_process_cloned: bool, optional

    :param halted: The run is halted, defaults to False.
    :type halted: bool, optional
    """

    NFA_NAME = "nfa_name"
    EVENT = "event"
    START_TIME = "start_time"
    START_STATE_NAME = "start_state_name"
    CURRENT_STATE_NAME = "current_state_name"
    RUN_ID = "run_id"
    VERSION = "version"
    HALTED = "halted"
    LAST_PROCESS_CLONED = "last_process_cloned"

    def __init__(self,
                 buffer: SharedVersionedMatchBuffer,
                 nfa: BoboNFA,
                 event: BoboEvent,
                 start_time: int = None,
                 start_state: BoboState = None,
                 current_state: BoboState = None,
                 parent_run: 'BoboRun' = None,
                 run_id: str = None,
                 version: RunVersion = None,
                 put_event: bool = True,
                 last_process_cloned: bool = False,
                 halted: bool = False) -> None:

        super().__init__()

        self.buffer = buffer
        self.nfa = nfa
        self.event = event
        self.start_time = start_time if start_time is not None \
            else event.timestamp
        self.start_state = start_state if start_state is not None \
            else self.nfa.start_state
        self.current_state = current_state if current_state is not None \
            else self.start_state
        self.id = BoboRun._generate_id(
            nfa_name=self.nfa.name,
            start_event_id=self.event.event_id) \
            if run_id is None else run_id
        self.version = version
        self._last_process_cloned = last_process_cloned
        self._halted = halted
        self._final = False
        self._subs = []
        self._lock = RLock()

        if parent_run is None:
            # create new version and add new event under this version
            if self.version is None:
                self.version = RunVersion()
                self.version.add_level(self.id)

            if put_event:
                self.buffer.put_event(
                    nfa_name=self.nfa.name,
                    run_id=self.id,
                    version=self.version.get_version_as_str(),
                    state_label=self.current_state.label,
                    event=self.event)

        else:
            # create version from existing, and
            # put and link last event to new version
            if self.version is None:
                self.version = RunVersion(
                    parent_version=parent_run.version)
                self.version.add_level(self.id)

            if put_event:
                self.buffer.put_event(
                    nfa_name=self.nfa.name,
                    run_id=parent_run.id,
                    version=parent_run.version.get_version_as_str(),
                    state_label=self.current_state.label,
                    event=self.event,
                    new_run_id=self.id,
                    new_version=self.version.get_version_as_str())

        # immediately final if start state is final state
        if self.nfa.start_is_final:
            self.set_final(history=None, notify=False)

    @staticmethod
    def _generate_id(nfa_name: str, start_event_id: str) -> str:
        """
        Generates a run ID.

        :param nfa_name: The run NFA name.
        :type nfa_name: str

        :param start_event_id: The ID of the first event in the run,
        :type start_event_id: str

        :return: A run ID.
        """

        return "{}-{}".format(nfa_name, start_event_id)

    def process(self, event: BoboEvent, recent: List[BoboEvent]) -> None:
        """
        Process an event.

        :param event: The event to process.
        :type event: BoboEvent

        :param recent: Recently accepted complex events of the corresponding
                        automaton.
        :type recent: List[BoboEvent]

        :raises RuntimeError: Run has already halted.
        """
        with self._lock:
            if self._halted:
                raise RuntimeError("Run {} has already halted."
                                   .format(self.id))

            # get the history of the current run
            history = self.buffer.get_all_events(
                self.nfa.name,
                self.id,
                self.version)

            if self._any_preconditions_failed(event, history, recent) or \
                    self._any_haltconditions_passed(event, history, recent):
                self.set_halt()
            else:
                self._handle_state(self.current_state, event, history, recent)

    def last_process_cloned(self) -> bool:
        """
        :return: True if the last time the run processed an event, a clone
                 occurred, False otherwise.
        """

        return self._last_process_cloned

    def set_cloned(self) -> None:
        """Set the run as having been cloned."""

        self._last_process_cloned = True

    def is_halted(self) -> bool:
        """
        :return: True if the run has halted, False otherwise.
        """

        with self._lock:
            return self._halted

    def is_final(self) -> bool:
        """
        :return: True if run has reached its final state, False otherwise.
        """

        with self._lock:
            return self._final

    def set_halt(self, notify: bool = True) -> None:
        """
        Halt the run.

        :param notify: Whether to notify run subscribers of the halting,
                       defaults to True.
        :type notify: bool, optional
        """

        with self._lock:
            if not self._halted:
                self._halted = True

                if notify:
                    self._notify_halt()

    def set_final(self,
                  history: BoboHistory = None,
                  notify: bool = True) -> None:
        """
        Put run into final state.

        :param history: The history of the run.
        :type history: BoboHistory

        :param notify: Whether to notify subscribers of the transition to
                       its final state, defaults to True.
        :type notify: bool, optional
        """

        with self._lock:
            if not self._final:
                if notify:
                    self._notify_final(
                        history if history is not None else
                        self.buffer.get_all_events(
                            nfa_name=self.nfa.name,
                            run_id=self.id,
                            version=self.version))

                # do not notify halt if final
                self.set_halt(notify=False)

                self._final = True

    def subscribe(self, subscriber: IRunSubscriber) -> None:
        """
        :param subscriber: Subscribes to the run.
        :type subscriber: IRunSubscriber
        """

        with self._lock:
            if subscriber not in self._subs:
                self._subs.append(subscriber)

    def unsubscribe(self, unsubscriber: IRunSubscriber) -> None:
        """
        :param unsubscriber: Unsubscribes from the run.
        :type unsubscriber: IRunSubscriber

        :raises RuntimeError: Run has already halted.
        """

        with self._lock:
            if unsubscriber in self._subs:
                self._subs.remove(unsubscriber)

    def to_dict(self) -> dict:
        """
        :return: A dict representation of the object.
        """

        with self._lock:
            return {
                self.NFA_NAME: self.nfa.name,
                self.EVENT: self.event.to_dict(),
                self.START_TIME: self.start_time,
                self.START_STATE_NAME: self.start_state.name,
                self.CURRENT_STATE_NAME: self.current_state.name,
                self.RUN_ID: self.id,
                self.VERSION: copy(self.version._levels),
                self.HALTED: self._halted,
                self.LAST_PROCESS_CLONED: self._last_process_cloned
            }

    def _handle_state(self,
                      state: BoboState,
                      event: BoboEvent,
                      history: BoboHistory,
                      recent: List[BoboEvent]) -> None:
        transition = self.nfa.transitions.get(state.name)

        if transition is None:
            raise RuntimeError("No transition found for state {}."
                               .format(state.name))

        for trans_state_name in transition.state_names:
            # get transition state from NFA
            trans_state = self.nfa.states[trans_state_name]

            # state successfully fulfilled
            if trans_state.process(event, history, recent):
                # negated i.e. should NOT have occurred, so halt
                if trans_state.is_negated:
                    self.set_halt()
                    break

                if not transition.is_deterministic:
                    # not a self loop: clone run
                    if trans_state_name != state.name:
                        self._notify_clone(trans_state, event)
                        self._last_process_cloned = True
                    else:
                        # increment current run
                        history = self._proceed(
                            event=event,
                            original_state=state,
                            trans_state=trans_state,
                            increment=self._last_process_cloned)
                        self._last_process_cloned = False
                else:
                    # deterministic: proceed as normal
                    history = self._proceed(event, state, trans_state)
            else:
                # if optional, or if state is negated: move to the next state
                if transition.is_deterministic and \
                        (trans_state.is_optional or trans_state.is_negated):
                    self._handle_state(trans_state, event, history, recent)

                # halt if requires strict contiguity
                elif transition.is_strict:
                    self.set_halt()
                    break

    def _proceed(self,
                 event: BoboEvent,
                 original_state: BoboState,
                 trans_state: BoboState,
                 increment: bool = False,
                 notify: bool = True) -> BoboHistory:

        if original_state.name not in self.nfa.states.keys():
            raise RuntimeError(
                "Original state {} not in NFA {}.".format(
                    original_state.name, self.nfa.name))

        if trans_state.name not in self.nfa.states.keys():
            raise RuntimeError(
                "Transition state {} not in NFA {}.".format(
                    original_state.name, self.nfa.name))

        if increment:
            new_increment = BoboRun._generate_id(
                nfa_name=self.nfa.name,
                start_event_id=event.event_id)
            new_version = self.version.list_to_version_str(
                self.version.get_version_as_list()[:-1] + [new_increment])
        else:
            new_increment = None
            new_version = None

        # add new event to buffer
        self.buffer.put_event(
            nfa_name=self.nfa.name,
            run_id=self.id,
            version=self.version.get_version_as_str(),
            state_label=trans_state.label,
            event=event,
            new_version=new_version)

        # (maybe) apply increment
        if new_increment is not None:
            self.version.increment_level(new_increment)

        # get run history
        new_history = self.buffer.get_all_events(
            self.nfa.name,
            self.id,
            self.version)

        # halt if final, else transition
        if self.nfa.final_state.name == trans_state.name:
            self.set_final(new_history, notify=notify)

        elif notify:
            self._notify_transition(
                original_state.name,
                trans_state.name,
                event)

        # update run
        self.current_state = trans_state
        self.event = event

        return new_history

    def _any_preconditions_failed(self,
                                  event: BoboEvent,
                                  history: BoboHistory,
                                  recent: List[BoboEvent]) -> bool:
        """If any preconditions are False, return True."""

        return any(not p.evaluate(event, history, recent)
                   for p in self.nfa.preconditions)

    def _any_haltconditions_passed(self,
                                   event: BoboEvent,
                                   history: BoboHistory,
                                   recent: List[BoboEvent]) -> bool:
        """If any haltconditions are True, return True."""

        return any(p.evaluate(event, history, recent)
                   for p in self.nfa.haltconditions)

    def _notify_transition(self,
                           state_name_from: str,
                           state_name_to: str,
                           event: BoboEvent) -> None:
        for subscriber in self._subs:
            subscriber.on_run_transition(
                run_id=self.id,
                state_name_from=state_name_from,
                state_name_to=state_name_to,
                event=event,
                notify=True)

    def _notify_clone(self,
                      state: BoboState,
                      next_event: BoboEvent) -> None:
        for subscriber in self._subs:
            subscriber.on_run_clone(
                state_name=state.name,
                event=next_event,
                parent_run_id=self.id,
                force_parent=False,
                notify=True)

    def _notify_final(self,
                      history: BoboHistory) -> None:
        for subscriber in self._subs:
            subscriber.on_run_final(
                run_id=self.id,
                history=history,
                notify=True)

    def _notify_halt(self) -> None:
        for subscriber in self._subs:
            subscriber.on_run_halt(
                run_id=self.id,
                notify=True)
