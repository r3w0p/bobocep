# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from time import time_ns

from bobocep.event.event_id.bobo_event_id import \
    BoboEventID


class BoboEventIDUnique(BoboEventID):

    def __init__(self):
        super().__init__()

        self._last: int = 0
        self._count: int = 0

    def generate(self) -> str:
        time: int = time_ns()

        if time == self._last:
            self._count += 1
        else:
            self._count = 1
            self._last = time

        return "{}_{}".format(time, self._count)
