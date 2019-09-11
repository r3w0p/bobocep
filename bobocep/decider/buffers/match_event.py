from typing import Dict, Tuple

from bobocep.rules.events.bobo_event import BoboEvent


class MatchEvent:
    """
    A BoboEvent instance that has been selected as a match for some state
    criteria by one or more runs.

    :param nfa_name: The name of the BoboNFA instance.
    :type nfa_name: str

    :param label: The state label with which the event is associated.
    :type label: str

    :param event: The event selected as being a match for some state.
    :type event: BoboEvent

    :param next_ids: Matches from older states, to which this event links,
                     defaults to an empty dict.
    :type next_ids: Dict[str, str], optional

    :param previous_ids: Matches from newer states, to which this event
                         links, default to an empty dict.
    :type previous_ids: Dict[str, str], optional
    """

    NFA_NAME = "nfa_name"
    LABEL = "label"
    EVENT = "event"
    NEXT_IDS = "next_ids"
    PREVIOUS_IDS = "previous_ids"

    def __init__(self,
                 nfa_name: str,
                 label: str,
                 event: BoboEvent,
                 next_ids: Dict[str, Tuple[str, str]] = None,
                 previous_ids: Dict[str, Tuple[str, str]] = None) -> None:
        super().__init__()

        self.nfa_name = nfa_name
        self.label = label
        self.event = event
        self.next_ids = {} if next_ids is None else next_ids
        self.previous_ids = {} if previous_ids is None else previous_ids

    def add_pointer_next(self,
                         version: str,
                         label: str = "",
                         event_id: str = "") -> None:
        """
        Points match event to the next match event ID using a run version.

        :param version: The run version.
        :type version: str

        :param label: The state label, defaults to an empty string.
        :type label: str, optional

        :param event_id: The event ID to point to, defaults to an empty string.
        :type event_id: str, optional

        :raises RuntimeError: Label and event ID are the same as those in the
                              match event i.e. attempt to point match event to
                              itself.
        """

        if label == self.label and event_id == self.event.event_id:
            raise RuntimeError("Cannot point match event to itself.")

        self.next_ids[version] = (label, event_id)

    def add_pointer_previous(self,
                             version: str,
                             label: str = "",
                             event_id: str = "") -> None:
        """
        Points match event to the previous match event ID using a run version.

        :param version: The run version.
        :type version: str

        :param label: The state label, defaults to an empty string.
        :type label: str, optional

        :param event_id: The event ID to point to, defaults to an empty string.
        :type event_id: str, optional

        :raises RuntimeError: Label and event ID are the same as those in the
                              match event i.e. attempt to point match event to
                              itself.
        """

        if label == self.label and event_id == self.event.event_id:
            raise RuntimeError("Cannot point match event to itself.")

        self.previous_ids[version] = (label, event_id)

    def remove_all_pointers(self, version: str) -> None:
        """
        Removes all pointers to a match event with a given run version.

        :param version: The run version.
        :type version: str
        """

        self.next_ids.pop(version, None)
        self.previous_ids.pop(version, None)

    def has_pointers(self) -> bool:
        """
        :return: True if the match event points to any other match events,
                 False otherwise.
        """

        return len(self.next_ids) > 0 or len(self.previous_ids) > 0

    def to_dict(self) -> dict:
        """
        :return: A dict representation of the object.
        """

        return {
            self.NFA_NAME: self.nfa_name,
            self.LABEL: self.label,
            self.EVENT: self.event.to_dict(),
            self.NEXT_IDS: self.next_ids,
            self.PREVIOUS_IDS: self.previous_ids
        }
