# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from time import time

from bobocep.event.event_id.bobo_event_id import \
    BoboEventID


class BoboEventIDUnique(BoboEventID):

    def __init__(self):
        super().__init__()

        self._last: int = 0
        self._count: int = 0

    def generate(self) -> str:
        now: int = int(time())

        if now == self._last:
            self._count += 1
        else:
            self._count = 1
            self._last = now

        return "{}_{}".format(now, self._count)
