# Copyright (c) The BoboCEP Authors
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License v3.0.

from typing import List

from bobocep.engine.receiver.validator.bobo_validator import BoboValidator
from bobocep.events.bobo_event import BoboEvent


class BoboValidatorType(BoboValidator):
    """Validates whether the type of the entity matches any of the given data
    types. If the entity is a BoboEvent, the event's data are checked.

    :param types: A list of valid data types.
    :type types: List[type]

    :param subtype: If True, will match subtypes of a type, equivalent to
                     isinstance() functionality.
                     If False, will match exact types only, equivalent to
                     type() functionality.
    :type subtype: bool
    """

    def __init__(self,
                 types: List[type],
                 subtype: bool = True):
        super().__init__()

        self._types = types
        self._subtype = subtype

    def is_valid(self, entity) -> bool:
        if isinstance(entity, BoboEvent):
            data = entity.data
        else:
            data = entity

        if self._subtype:
            return any(isinstance(data, t) for t in self._types)
        else:
            return any(type(data) == t for t in self._types)
