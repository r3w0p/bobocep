from abc import ABC, abstractmethod
from dpcontracts import require, ensure


class BoboRule(ABC):
    """An abstract rule."""

    @abstractmethod
    @ensure("result must be a dict",
            lambda args, result: isinstance(result, dict))
    def to_dict(self) -> dict:
        """
        :return: A dict representation of the object.
        """

    @staticmethod
    @abstractmethod
    @require("'d' must be a dict",
             lambda args: isinstance(args.d, dict))
    @ensure("result must be an instance of BoboRule",
            lambda args, result: isinstance(result, BoboRule))
    def from_dict(d: dict) -> 'BoboRule':
        """
        :return: An object from a dict representation.
        """
