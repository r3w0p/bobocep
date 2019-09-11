from typing import Dict

from bobocep.rules.events.bobo_event import BoboEvent


class PrimitiveEvent(BoboEvent):
    """A primitive event.

    :param timestamp: The event timestamp indicating when it was first
                      generated.
    :type timestamp: int

    :param data: The event data, defaults to an empty dict.
    :type data: Dict[str, str], optional

    :param event_id: The event ID, defaults to a randomly generated ID.
    :type event_id: str, optional
    """

    def __init__(self,
                 timestamp: int,
                 data: Dict[str, str] = None,
                 event_id: str = None) -> None:
        super().__init__(timestamp=timestamp,
                         data=data,
                         event_id=event_id)

    def to_dict(self) -> dict:
        """
        :return: A dict representation of the object.
        """

        return {
            self.TIMESTAMP: self.timestamp,
            self.DATA: self.data,
            self.EVENT_ID: self.event_id
        }
