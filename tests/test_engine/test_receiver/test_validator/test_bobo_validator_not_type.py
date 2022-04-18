from datetime import datetime

from bobocep.engine.receiver.validator.bobo_validator_not_type import \
    BoboValidatorNotType
from bobocep.events.bobo_event_primitive import BoboEventPrimitive


class TestClassType:
    def __init__(self):
        super().__init__()


class TestClassSubtype(TestClassType):
    def __init__(self):
        super().__init__()


def test_1_type_dict_valid():
    validator = BoboValidatorNotType(types=[dict])

    assert validator.is_valid(entity=None)
    assert validator.is_valid(entity="abc")
    assert validator.is_valid(entity=123)


def test_1_type_dict_invalid():
    validator = BoboValidatorNotType(types=[dict])

    assert not validator.is_valid(entity={})
    assert not validator.is_valid(entity={"key": None})
    assert not validator.is_valid(entity={"key": 123})


def test_1_type_str_event_data_valid_only():
    validator = BoboValidatorNotType(types=[str])

    assert validator.is_valid(entity=BoboEventPrimitive(
        event_id="id", timestamp=datetime.now(), data=123))

    assert validator.is_valid(entity=BoboEventPrimitive(
        event_id="id", timestamp=datetime.now(), data=None))


def test_1_type_str_event_data_invalid_only():
    validator = BoboValidatorNotType(types=[str])

    assert not validator.is_valid(entity=BoboEventPrimitive(
        event_id="id", timestamp=datetime.now(), data=""))

    assert not validator.is_valid(entity=BoboEventPrimitive(
        event_id="id", timestamp=datetime.now(), data="abc"))


def test_1_type_subtype_true_invalid():
    validator = BoboValidatorNotType(types=[TestClassType])

    assert not validator.is_valid(entity=TestClassType())
    assert not validator.is_valid(entity=TestClassSubtype())


def test_1_type_subtype_false_valid():
    validator = BoboValidatorNotType(types=[TestClassType], subtype=False)

    assert validator.is_valid(entity=TestClassSubtype())


def test_1_type_subtype_false_invalid():
    validator = BoboValidatorNotType(types=[TestClassType], subtype=False)

    assert not validator.is_valid(entity=TestClassType())
