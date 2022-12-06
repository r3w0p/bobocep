# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from typing import Tuple, List

from src.cep.engine.receiver.validator.bobo_validator import BoboValidator
from src.cep.event.bobo_event import BoboEvent


class BoboValidatorNotType(BoboValidator):
    """Validates whether the type of the entity does not match any of the given
    data types. If the entity is a BoboEvent, the event's data are checked."""

    def __init__(self,
                 types: List[type],
                 subtype: bool = True):
        super().__init__()

        self._types: Tuple[type, ...] = tuple(types)
        self._subtype = subtype

    def is_valid(self, entity) -> bool:
        if isinstance(entity, BoboEvent):
            data = entity.data
        else:
            data = entity

        if self._subtype:
            return not any(isinstance(data, t) for t in self._types)
        else:
            return not any(type(data) == t for t in self._types)
