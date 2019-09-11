from bobocep.decider.buffers.match_event import MatchEvent
from bobocep.decider.versions.run_version import RunVersion
from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory


class SharedVersionedMatchBuffer:
    """
    An event buffer based on the Shared Versioned Match Buffer proposed by
    Agrawal et al. (2008) in their paper "Efficient Pattern Matching over
    Event Streams".

    The buffer stores events for partially completed runs.
    A BoboEvent instance is stored within a MatchEvent instance that provides
    a means of linking BoboEvents that can be used by one or more runs.
    The next event in a MatchEvent link points to an earlier event accepted by
    a run.
    Traversing the next links will identify all events for a given run.
    """

    NFA_NAME = "nfa_name"
    LABEL = "label"
    MATCH_EVENT = "match_event"
    RUN_ID = "run_id"
    VERSION = "version"
    EVENT_ID = "event_id"
    EVENTS = "events"
    LAST = "last"

    def __init__(self) -> None:
        super().__init__()

        # BoboNFA Name -> BoboState Label -> BoboEvent ID -> MatchEvent
        self._eve = {}

        # BoboNFA Name -> BoboRun ID -> RunVersion -> Last MatchEvent
        self._ver = {}

    @staticmethod
    def _get_or_create_subdict(d: dict, key: str) -> dict:
        """
        Gets a nested dict inside an existing dict, or creates one there if one
        does not exist.

        :param d: The dict in which to create a dict.
        :type d: dict

        :param key: The key that will point to the new dict.
        :type key: str

        :return: The nested dict.
        """
        if key not in d:
            d[key] = {}

        return d.get(key)

    def get_event(self,
                  nfa_name: str,
                  state_label: str,
                  event_id: str,
                  default=None) -> BoboEvent:
        """
        Get a BoboEvent instance from the buffer.

        :param nfa_name: The NFA name,
        :type nfa_name: str

        :param state_label: The state label.
        :type state_label: str

        :param event_id: The event ID.
        :type event_id: str

        :param default: The default value, defaults to None.
        :type default: any, optional

        :return: The BoboEvent instance,
                 or default value if an event is not found.
        """

        try:
            return self._eve[nfa_name][state_label][event_id].event

        except KeyError:
            return default

    def put_event(self,
                  nfa_name: str,
                  run_id: str,
                  version: str,
                  state_label: str,
                  event: BoboEvent,
                  new_run_id: str = None,
                  new_version: str = None) -> MatchEvent:
        """
        Puts a BoboEvent instance into the buffer.

        :param nfa_name: The BoboNFA instance name.
        :type nfa_name: str

        :param run_id: The run ID with which to associate the event.
        :type run_id: str

        :param version: The run version of the run with which to associate the
                        event.
        :type version: str

        :param state_label: The label of the state .
        :type state_label: str

        :param event: The event to add to the buffer.
        :type event: BoboEvent

        :param new_run_id: The new run ID with which to associate the event,
                           so that the other run ID will point to this one,
                           defaults to None.
        :type new_run_id: str, optional

        :param new_version: The new run version with which to associate the
                            event, so that the other version will point to this
                            one, defaults to None.
        :type new_version: str, optional

        :return: A MatchEvent instance containing the BoboEvent instance.
        """

        # get match events for this nfa, keyed by the bobo event they represent
        nfa_labels = self._get_or_create_subdict(self._eve, nfa_name)
        nfa_events = self._get_or_create_subdict(nfa_labels, state_label)

        # look for bobo event in buffer, or add a new match event for it
        # if a match event isn't found
        if event.event_id not in nfa_events:
            nfa_events[event.event_id] = MatchEvent(
                nfa_name=nfa_name,
                label=state_label,
                event=event)

        new_match_event = nfa_events[event.event_id]

        # get last event under the original run ID and version
        # before (maybe) updating run ID and version
        last_match_event = self.get_last_event(
            nfa_name=nfa_name,
            run_id=run_id,
            version=version)

        if new_run_id is not None:
            run_id = new_run_id

        if new_version is not None:
            version = new_version

        # point the (maybe new) run ID and version to the next match event
        nfa_runs = self._get_or_create_subdict(self._ver, nfa_name)
        run_versions = self._get_or_create_subdict(nfa_runs, run_id)
        run_versions[version] = new_match_event

        # point new match event to the last match event, if it exists
        if last_match_event is not None:
            # points to the last match event
            new_match_event.add_pointer_next(
                version=version,
                label=last_match_event.label,
                event_id=last_match_event.event.event_id)

            # points backwards to the new match event
            last_match_event.add_pointer_previous(
                version=version,
                label=new_match_event.label,
                event_id=new_match_event.event.event_id)
        else:
            # adds pointer to nothing, so run is still linked to event
            new_match_event.add_pointer_next(version=version)

        return new_match_event

    def remove_version(self, nfa_name: str, version: str) -> None:
        """
        Removes a run version from all of the match events in the buffer.

        :param nfa_name: The name of the BoboNFA instance.
        :type nfa_name: str

        :param version: The run version.
        :type version: str
        """

        # remove version from runs
        nfa_runs = self._ver.get(nfa_name)

        if nfa_runs is not None:
            for nfa_run in tuple(nfa_runs.values()):
                for run_version in tuple(nfa_run.keys()):
                    if version == run_version:
                        nfa_runs.pop(version, None)

        # remove pointers in events, and maybe event itself
        nfa_labels = self._eve.get(nfa_name)

        if nfa_labels is not None:
            for match_events in tuple(nfa_labels.values()):
                for match_event in tuple(match_events.values()):
                    match_event.remove_all_pointers(version)

                    # drop more pointers, drop event
                    if not match_event.has_pointers():
                        self._eve \
                            .get(nfa_name) \
                            .get(match_event.label) \
                            .pop(match_event.event.event_id, None)

    def get_last_event(self,
                       nfa_name: str,
                       run_id: str,
                       version: str,
                       default=None) -> MatchEvent:
        """
        Gets the last match event.

        :param nfa_name: The BoboNFA instance name.
        :type nfa_name: str

        :param run_id: The run ID.
        :type run_id: str

        :param version: The run version.
        :type version: str

        :param default: A value to return if no match event is found,
                        defaults to None.
        :type default: any, optional

        :return: The last match event,
                 or a default value if one does not exist.
        """

        try:
            return self._ver[nfa_name][run_id][version]

        except KeyError:
            return default

    def get_all_events(self,
                       nfa_name: str,
                       run_id: str,
                       version: RunVersion) -> BoboHistory:
        """
        Gets all events associated with a run and compiles them into a
        BoboHistory instance.

        :param nfa_name: The BoboNFA instance name.
        :type nfa_name: str

        :param run_id: The run ID.
        :type run_id: str

        :param version: The run version.
        :type version: RunVersion

        :return: A BoboHistory instance with all of the events in it.
        """

        all_events = {}
        current_level = 0
        current_incr = 0
        current_version = version.get_version_as_str()

        # start with the latest match event
        current_event = self.get_last_event(
            nfa_name=nfa_name,
            run_id=run_id,
            version=current_version)

        while True:
            if current_event is not None:
                # add event to dict, keyed under the label name
                if current_event.label not in all_events:
                    all_events[current_event.label] = []
                all_events[current_event.label].insert(0, current_event.event)

                # get next match event using current version
                next_event = self._get_next_event(
                    event=current_event,
                    nfa_name=nfa_name,
                    version_str=current_version)

                # no event found under current version
                if next_event is None:
                    # get previous version by decreasing increment
                    current_incr += 1
                    current_version = \
                        version.get_previous_version_as_str(
                            decrease_level=current_level,
                            decrease_incr=current_incr)

                    # get previous version by decreasing level
                    if current_version is None:
                        current_level += 1
                        current_incr = 0
                        current_version = \
                            version.get_previous_version_as_str(
                                decrease_level=current_level,
                                decrease_incr=current_incr)

                        # no previous version, stop search
                        if current_version is None:
                            break

                    # attempt to find next event with new version
                    next_event = self._get_next_event(
                        event=current_event,
                        nfa_name=nfa_name,
                        version_str=current_version)

                    if next_event is None:
                        break

                current_event = next_event
            else:
                break

        return BoboHistory(events=all_events)

    def _get_next_event(self,
                        event: MatchEvent,
                        nfa_name: str,
                        version_str: str):
        try:
            next_tuple = event.next_ids.get(version_str)
            if next_tuple is not None:
                next_event = self._eve[nfa_name][next_tuple[0]][next_tuple[1]]
            else:
                next_event = None
        except KeyError:
            next_event = None

        return next_event

    def to_dict(self) -> dict:
        """
        :return: A dict representation of the object.
        """

        eve = []
        ver = []

        for nfa_name, nfa_dict in self._eve.items():
            for event_dict in nfa_dict.values():
                for match_event in event_dict.values():
                    eve.append({
                        self.NFA_NAME: nfa_name,
                        self.MATCH_EVENT: match_event.to_dict()
                    })

        for nfa_name, nfa_dict in self._ver.items():
            for run_id, run_dict in nfa_dict.items():
                for version, match_event in run_dict.items():
                    ver.append({
                        self.NFA_NAME: nfa_name,
                        self.LABEL: match_event.label,
                        self.RUN_ID: run_id,
                        self.VERSION: version,
                        self.EVENT_ID: match_event.event.event_id
                    })

        return {
            self.EVENTS: eve,
            self.LAST: ver
        }
