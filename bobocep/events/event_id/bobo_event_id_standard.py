# Copyright (c) 2022, The BoboCEP Contributors
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License v3.0.

from time import time_ns
from uuid import uuid4

from bobocep.events.event_id.bobo_event_id import \
    BoboEventID


class BoboEventIDStandard(BoboEventID):

    def __init__(self):
        super().__init__()

    def generate(self) -> str:
        return "{}_{}".format(time_ns(), uuid4())
