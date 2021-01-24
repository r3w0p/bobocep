from abc import ABC, abstractmethod
from dpcontracts import require, ensure


class BoboRule(ABC):
    """A :code:`bobocep` rule."""

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
    def from_dict(self, d: dict) -> 'BoboRule':
        """
        :return: An object from a dict representation.
        """
