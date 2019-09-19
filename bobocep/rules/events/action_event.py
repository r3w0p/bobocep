from typing import Dict

from bobocep.rules.events.bobo_event import BoboEvent


class ActionEvent(BoboEvent):
    """An action event.

    :param timestamp: The event timestamp indicating when it was first
                      generated.
    :type timestamp: int

    :param name: The action name.
    :type name: str

    :param success: :code:`True` if action was successfully executed,
                    :code:`False` otherwise.
    :type success: bool

    :param for_event: The event for which the action was triggered.
    :type for_event: BoboEvent

    :param exception: The name of an exception, if one was raised during
                      action execution. Defaults to an empty string.
    :type exception: str, optional

    :param description: The description provided with an exception, if one was
                        raised. Defaults to an empty string.
    :type description: str, optional

    :param data: The event data, defaults to an empty dict.
    :type data: Dict[str, str], optional

    :param event_id: The event ID, defaults to a randomly generated ID.
    :type event_id: str, optional
    """

    NAME = "name"
    SUCCESS = "success"
    FOR_EVENT = "for_event"
    EXCEPTION = "exception"
    DESCRIPTION = "description"

    def __init__(self,
                 timestamp: int,
                 name: str,
                 success: bool,
                 for_event: BoboEvent,
                 exception: str = None,
                 description: str = None,
                 data: Dict[str, str] = None,
                 event_id: str = None) -> None:
        super().__init__(timestamp=timestamp,
                         data=data,
                         event_id=event_id)

        self.name = name
        self.success = success
        self.for_event = for_event
        self.exception = exception if exception is not None else ""
        self.description = description if description is not None else ""

    def to_dict(self) -> dict:
        """
        :return: A dict representation of the object.
        """

        return {
            self.TIMESTAMP: self.timestamp,
            self.NAME: self.name,
            self.SUCCESS: self.success,
            self.FOR_EVENT: self.for_event.to_dict(),
            self.EXCEPTION: self.exception,
            self.DESCRIPTION: self.description,
            self.DATA: self.data,
            self.EVENT_ID: self.event_id
        }
