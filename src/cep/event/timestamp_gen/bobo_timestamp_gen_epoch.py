# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from time import time_ns


class BoboTimestampGenEpoch:

    def __init__(self):
        super().__init__()

    @staticmethod
    def generate() -> int:
        return time_ns() // 1000000
