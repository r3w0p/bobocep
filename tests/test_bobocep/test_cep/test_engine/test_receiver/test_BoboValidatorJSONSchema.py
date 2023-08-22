# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
import pytest

from bobocep.cep.engine.receiver.validator import BoboValidatorError, \
    BoboValidatorJSONSchema


SCHEMA_VALID: dict = {
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

SCHEMA_INVALID: str = "abc123"


class TestValid:

    def test_valid_schema_valid_instance(self):
        data: dict = {
            "forename": "Foo",
            "surname": "Bar"
        }

        validator = BoboValidatorJSONSchema(schema=SCHEMA_VALID)

        assert validator.is_valid(data=data)


class TestInvalid:

    def test_invalid_schema(self):
        data: dict = {}

        validator = BoboValidatorJSONSchema(schema=SCHEMA_INVALID)

        with pytest.raises(BoboValidatorError):
            assert validator.is_valid(data=data)

    def test_valid_schema_invalid_instance(self):
        data: dict = {
            "forename": "Foo"
        }

        validator = BoboValidatorJSONSchema(schema=SCHEMA_VALID)

        assert not validator.is_valid(data=data)
