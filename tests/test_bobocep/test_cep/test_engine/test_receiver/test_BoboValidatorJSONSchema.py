# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
import pytest

from bobocep.cep.validator.validator import BoboValidatorError, \
    BoboValidatorJSONSchema

SCHEMA_VALID_DICT: dict = {
  "type": "object",
  "required": ["forename", "surname"],
  "properties": {
    "forename": {
      "type": "string"
    },
    "surname": {
      "type": "string"
    }
  }
}

SCHEMA_INVALID_STR: str = "abc123"
# TODO other tests of invalid input: int, etc.


class TestValid:

    def test_valid_schema_valid_instance(self):
        data: dict = {
            "forename": "Foo",
            "surname": "Bar"
        }

        validator = BoboValidatorJSONSchema(schema=SCHEMA_VALID_DICT)

        assert validator.is_valid(data=data)


class TestInvalid:

    def test_invalid_schema_str(self):
        data: dict = {}

        validator = BoboValidatorJSONSchema(schema=SCHEMA_INVALID_STR)

        with pytest.raises(BoboValidatorError):
            validator.is_valid(data=data)

    def test_invalid_data_for_valid_schema(self):
        data: dict = {
            "forename": "Foo"
        }

        validator = BoboValidatorJSONSchema(schema=SCHEMA_VALID_DICT)

        assert not validator.is_valid(data=data)
