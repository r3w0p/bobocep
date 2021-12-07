from abc import ABC

from dpcontracts import require


class BoboEvent(ABC):
    """An abstract event.

    :param event_id: The event ID.
    :type event_id: str

    :param timestamp: The timestamp indicating when the event was recorded.
    :type timestamp: int

    :param data: The type of the event data.
    :type data: type

    :param data: The event data.
    """

    @require("'event_id' must be of type str",
             lambda args: isinstance(args.event_id, str))
    @require("'timestamp' must be of type int",
             lambda args: isinstance(args.timestamp, int))
    @require("'data_type' must be of type type",
             lambda args: isinstance(args.data_type, type))
    def __init__(self,
                 event_id: str,
                 timestamp: int,
                 data_type: type,
                 data):
        super().__init__()

        self.event_id = event_id
        self.timestamp = timestamp
        self.data_type = data_type
        self.data = data
