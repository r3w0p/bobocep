from abc import abstractmethod
from typing import Dict
from uuid import uuid4


class BoboEvent:
    """A :code:`bobocep` event.

    :param timestamp: The event timestamp indicating when it was first
                      generated.
    :type timestamp: int

    :param data: The event data, defaults to an empty dict.
    :type data: Dict[str, str], optional

    :param event_id: The event ID, defaults to a randomly generated ID.
    :type event_id: str, optional
    """

    TIMESTAMP = "timestamp"
    DATA = "data"
    EVENT_ID = "event_id"

    def __init__(self,
                 timestamp: int,
                 data: Dict[str, str] = None,
                 event_id: str = None) -> None:
        super().__init__()

        self.timestamp = timestamp
        self.data = {} if data is None else data
        self.event_id = '{}-{}'.format(uuid4(), timestamp) \
            if event_id is None else event_id

    @abstractmethod
    def to_dict(self) -> dict:
        """
        :return: A dict representation of the object.
        """
