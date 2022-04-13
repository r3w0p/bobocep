from typing import List

from bobocep.engine.receiver.validator.bobo_validator import BoboValidator
from bobocep.events.bobo_event import BoboEvent


class BoboValidatorNotType(BoboValidator):
    """Validates whether the type of the entity does not match any of the given
    data types. If the entity is a BoboEvent, the event's data are checked.

    :param list_types: A list of valid data types.
    :type list_types: List[type]

    :param subclass: If True, will match subclasses of a type, equivalent to
                     isinstance() functionality.
                     If False, will match exact types only, equivalent to
                     type() functionality.
    :type subclass: bool
    """

    def __init__(self,
                 list_types: List[type],
                 subclass: bool = True):
        super().__init__()

        self._list_types = list_types
        self._subclass = subclass

    def is_valid(self, entity) -> bool:
        if isinstance(entity, BoboEvent):
            data = entity.data
        else:
            data = entity

        if self._subclass:
            return not any(isinstance(data, data_type)
                           for data_type in self._list_types)
        else:
            return not any(type(data) == data_type
                           for data_type in self._list_types)
