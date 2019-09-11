from typing import Dict

from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory


class CompositeEvent(BoboEvent):
    """A composite event.

    :param timestamp: The event timestamp indicating when it was first
                      generated.
    :type timestamp: int

    :param name: The event name.
    :type name: str

    :param history: The history of events that caused the composite event to be
                    generated.
    :type history: BoboHistory

    :param data: The event data, defaults to an empty dict.
    :type data: Dict[str, str], optional

    :param event_id: The event ID, defaults to a randomly generated ID.
    :type event_id: str, optional
    """

    NAME = "name"
    HISTORY = "history"

    def __init__(self,
                 timestamp: int,
                 name: str,
                 history: BoboHistory,
                 data: Dict[str, str] = None,
                 event_id: str = None) -> None:
        super().__init__(timestamp=timestamp,
                         data=data,
                         event_id=event_id)

        self.name = name
        self.history = history

    def to_dict(self) -> dict:
        """
        :return: A dict representation of the object.
        """

        return {
            self.TIMESTAMP: self.timestamp,
            self.NAME: self.name,
            self.HISTORY: self.history.to_dict(),
            self.DATA: self.data,
            self.EVENT_ID: self.event_id
        }
