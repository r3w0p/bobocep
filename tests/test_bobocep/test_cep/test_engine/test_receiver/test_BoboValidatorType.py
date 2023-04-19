# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from bobocep.cep.engine.receiver.validator import BoboValidatorType
from bobocep.cep.event import BoboEventSimple
from bobocep.cep.gen.timestamp import BoboGenTimestampEpoch


class StubClassType:
    def __init__(self):
        super().__init__()


class StubClassSubtype(StubClassType):
    def __init__(self):
        super().__init__()


def test_1_type_dict_valid_only():
    validator = BoboValidatorType(types=[dict])

    assert validator.is_valid(data={})
    assert validator.is_valid(data={"key": None})
    assert validator.is_valid(data={"key": 123})


def test_1_type_dict_invalid_only():
    validator = BoboValidatorType(types=[dict])

    assert not validator.is_valid(data=None)
    assert not validator.is_valid(data="abc")
    assert not validator.is_valid(data=123)


def test_1_type_str_event_data_valid_only():
    validator = BoboValidatorType(types=[str])

    assert validator.is_valid(data=BoboEventSimple(
        event_id="id", timestamp=BoboGenTimestampEpoch().generate(), data=""))

    assert validator.is_valid(data=BoboEventSimple(
        event_id="id", timestamp=BoboGenTimestampEpoch().generate(),
        data="abc"))


def test_1_type_str_event_data_invalid_only():
    validator = BoboValidatorType(types=[str])

    assert not validator.is_valid(data=BoboEventSimple(
        event_id="id", timestamp=BoboGenTimestampEpoch().generate(),
        data=None))

    assert not validator.is_valid(data=BoboEventSimple(
        event_id="id", timestamp=BoboGenTimestampEpoch().generate(), data=123))

    assert not validator.is_valid(data=BoboEventSimple(
        event_id="id", timestamp=BoboGenTimestampEpoch().generate(),
        data={"key": 123}))


def test_1_type_subtype_false_valid():
    validator = BoboValidatorType(types=[StubClassType], subtype=False)

    assert validator.is_valid(data=StubClassType())


def test_1_type_subtype_false_invalid():
    validator = BoboValidatorType(types=[StubClassType], subtype=False)

    assert not validator.is_valid(data=StubClassSubtype())
