# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from typing import Tuple, List, Any

from src.cep.engine.receiver.validator.bobo_validator import BoboValidator
from src.cep.event.bobo_event import BoboEvent


class BoboValidatorType(BoboValidator):
    """Validates whether the entity type matches any of the given data types.
    If the data are a BoboEvent, then the event's data are checked instead."""

    def __init__(self,
                 types: List[type],
                 subtype: bool = True):
        super().__init__()

        self._types: Tuple[type, ...] = tuple(types)
        self._subtype = subtype

    def is_valid(self, data: Any) -> bool:
        if isinstance(data, BoboEvent):
            data = data.data

        if self._subtype:
            return any(isinstance(data, t) for t in self._types)
        else:
            return any(type(data) == t for t in self._types)
