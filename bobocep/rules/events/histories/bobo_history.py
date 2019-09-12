from typing import Dict, List

from bobocep.rules.events.bobo_event import BoboEvent


class BoboHistory:
    """A :code:`bobocep` event history.

    :param events: The current history of events, where each key is a label
                   with which a list of events are associated,
                   defaults to an empty dict.
    :type events: Dict[str, List[BoboEvent]], optional
    """

    def __init__(self, events: Dict[str, List[BoboEvent]] = None) -> None:
        super().__init__()

        self.events = {} if events is None else events
        self.first = None
        self.last = None

        for event_list in self.events.values():
            for event in event_list:
                if self.first is None or \
                        event.timestamp < self.first.timestamp:
                    self.first = event

                if self.last is None or event.timestamp > self.last.timestamp:
                    self.last = event

    def to_dict(self) -> dict:
        """
        :return: A dict representation of the object.
        """

        dict_history = {}

        for key in self.events.keys():
            key_events = self.events[key]

            dict_history[key] = []

            for event in key_events:
                dict_history[key].append(event.to_dict())

        return dict_history
