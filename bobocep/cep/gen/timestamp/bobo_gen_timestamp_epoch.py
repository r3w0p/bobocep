# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from time import time_ns

from bobocep.cep.gen.timestamp.bobo_gen_timestamp import BoboGenTimestamp


class BoboGenTimestampEpoch(BoboGenTimestamp):
    """A timestamp generator that returns the current time in milliseconds
    since the Epoch."""

    def __init__(self):
        super().__init__()

    def generate(self) -> int:
        return time_ns() // 1000000
