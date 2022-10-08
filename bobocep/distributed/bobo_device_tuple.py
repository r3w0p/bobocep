# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from typing import NamedTuple, Optional


class BoboDeviceTuple(NamedTuple):
    addr: str
    port: int
    urn: str
    id_key: str
