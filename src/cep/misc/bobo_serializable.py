# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from abc import ABC, abstractmethod
from typing import List, Tuple, Any, Optional

from src.cep.misc.bobo_serializable_error import BoboSerializableError


class BoboSerializable(ABC):

    @abstractmethod
    def to_dict(self) -> dict:
        """"""

    @staticmethod
    @abstractmethod
    def from_dict(d: dict) -> 'BoboSerializable':
        """"""

    @staticmethod
    def validate_dict(d: dict, keys: List[Tuple[str, Optional[type]]]) -> None:
        # TODO move into BoboEvent?
        for key, exp_type in keys:
            if key not in d:
                raise BoboSerializableError("Missing key '{}'.".format(key))

            if exp_type == None:
                continue

            fnd_type = type(d[key])
            if fnd_type != exp_type:
                raise BoboSerializableError(
                    "Invalid type for key '{}'. Expected '{}', found '{}'."
                    .format(key, exp_type, fnd_type))
