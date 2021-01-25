from abc import ABC, abstractmethod
from dpcontracts import require, ensure


class BoboSerializable(ABC):
    """An abstract serializable class."""

    @abstractmethod
    @ensure("result must be a dict",
            lambda args, result: isinstance(result, dict))
    def to_dict(self) -> dict:
        """
        :return: A dict representation of the object.
        :rtype: dict
        """

    @staticmethod
    @abstractmethod
    @require("'d' must be a dict",
             lambda args: isinstance(args.d, dict))
    @ensure("result must be an instance of BoboSerializable",
            lambda args, result: isinstance(result, BoboSerializable))
    def from_dict(d: dict) -> 'BoboSerializable':
        """
        :return: An object from a dict representation.
        :rtype: BoboSerializable
        """
