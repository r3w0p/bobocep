# Copyright (c) 2022, The BoboCEP Contributors
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License v3.0.

from bobocep.engine.receiver.validator.bobo_validator import BoboValidator


class BoboValidatorAll(BoboValidator):
    """Validator that accepts all data."""

    def __init__(self):
        super().__init__()

    def is_valid(self, entity) -> bool:
        return True
