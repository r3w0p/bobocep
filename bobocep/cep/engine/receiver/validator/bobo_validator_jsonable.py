# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import json
from typing import Any

from bobocep.cep.engine.receiver.validator.bobo_validator import BoboValidator
from bobocep.cep.event.bobo_event import BoboEvent


class BoboValidatorJSONable(BoboValidator):
    """Validates whether the data type is JSONable.
    If the data are a BoboEvent, then the event's data are checked instead."""

    def __init__(self):
        super().__init__()

    def is_valid(self, data: Any) -> bool:
        if isinstance(data, BoboEvent):
            data = data.data

        try:
            json.loads(data)

        except ValueError:
            return False

        return True
