# Copyright (c) 2019-2024 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Receiver data validators.
"""

from abc import ABC, abstractmethod
from json import dumps
from typing import Any, List, Tuple

from jsonschema import validate as jsonschema_validate  # type: ignore
from jsonschema.exceptions import ValidationError, SchemaError  # type: ignore

from bobocep import BoboError
from bobocep.cep.event import BoboEvent


class BoboValidatorError(BoboError):
    """
    A validator error.
    """


class BoboValidator(ABC):
    """An abstract validator."""

    @abstractmethod
    def is_valid(self, data: Any) -> bool:
        """
        :param data: Data to validate.
        :return: `True` if data are valid; `False` otherwise.
        """


class BoboValidatorAll(BoboValidator):
    """
    Validator that accepts all data.
    """

    def is_valid(self, data: Any) -> bool:
        """
        :return: Always returns `True`.
        """
        return True


class BoboValidatorJSONable(BoboValidator):
    """
    Validates whether the data type is JSONable. If the data are a
    BoboEvent, then the event's data are checked instead.
    """

    def is_valid(self, data: Any) -> bool:
        """
        :return: `True` if data are valid JSON; `False` otherwise.
        """
        if isinstance(data, BoboEvent):
            data = data.data

        try:
            dumps(data)

        except (RecursionError, TypeError, ValueError):
            return False

        return True


class BoboValidatorType(BoboValidator):
    """
    Validates whether the entity type matches any of the given data types.
    If the data are a BoboEvent, then the event's data are checked instead.
    """

    def __init__(self,
                 types: List[type],
                 subtype: bool = True):
        """
        :param types: The types of which the data must match at least one
            for the data to be valid.
        :param subtype: If `True`, subtypes of a type are also valid.
            If `False`, data must match exact type.
        """
        super().__init__()

        self._types: Tuple[type, ...] = tuple(types)
        self._subtype = subtype

    def is_valid(self, data: Any) -> bool:
        """
        :return: `True` if the data matches a type; `False` otherwise.
        """
        if isinstance(data, BoboEvent):
            data = data.data

        if self._subtype:
            return any(isinstance(data, t) for t in self._types)
        else:
            return any(type(data) == t for t in self._types)


class BoboValidatorJSONSchema(BoboValidatorJSONable):
    """
    Validates whether the data type is valid with respect to
    a given JSON Schema. If the data are a BoboEvent,
    then the event's data are checked instead.
    """

    def __init__(self, schema: dict):
        """
        :param schema: The JSON schema against which to compare data.
        """
        super().__init__()

        self._schema: dict = schema

    def is_valid(self, data: Any) -> bool:
        """
        :return: `True` if data are valid as per the JSON schema;
                 `False` otherwise.

        :raises: BoboValidatorError: Invalid JSON schema.
        """
        try:
            jsonschema_validate(instance=data, schema=self._schema)

        except ValidationError:
            return False

        except SchemaError as e:
            raise BoboValidatorError(e)

        return True
