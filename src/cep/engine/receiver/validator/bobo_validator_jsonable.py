# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from typing import Tuple, List

from src.cep.engine.receiver.validator.bobo_validator import BoboValidator
from src.cep.event.bobo_event import BoboEvent
import json


class BoboValidatorJSONable(BoboValidator):
    """Validates whether the type of the entity is JSONable.
    If the entity is a BoboEvent, the event's data are checked instead."""

    def __init__(self):
        super().__init__()

    def is_valid(self, entity) -> bool:
        if isinstance(entity, BoboEvent):
            data = entity.data
        else:
            data = entity

        try:
            json.loads(data)

        except ValueError:
            return False

        return True
