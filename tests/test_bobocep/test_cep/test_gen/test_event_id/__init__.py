# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from bobocep.cep.gen.event_id import BoboGenEventID


class BoboSameEveryTimeEventID(BoboGenEventID):
    """
    Produces the same ID string every time.
    Useful for testing whether an error is raised on duplicate IDs.
    """

    def __init__(self, id_str: str = "id_str"):
        super().__init__()

        self._id_str = id_str

    def generate(self) -> str:
        return self._id_str
