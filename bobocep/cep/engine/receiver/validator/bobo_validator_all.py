# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from bobocep.cep.engine.receiver.validator.bobo_validator import BoboValidator


class BoboValidatorAll(BoboValidator):
    """Validator that accepts all data."""

    def __init__(self):
        super().__init__()

    def is_valid(self, entity) -> bool:
        return True
