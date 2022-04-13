from datetime import datetime

from bobocep.engine.receiver.validator.bobo_validator_type import \
    BoboValidatorType
from bobocep.events.bobo_event_primitive import BoboEventPrimitive


def test_1_type_dict_valid_only():
    validator = BoboValidatorType(types=[dict])

    assert validator.is_valid(entity={})
    assert validator.is_valid(entity={"key": None})
    assert validator.is_valid(entity={"key": 123})


def test_1_type_dict_invalid_only():
    validator = BoboValidatorType(types=[dict])

    assert not validator.is_valid(entity=None)
    assert not validator.is_valid(entity="abc")
    assert not validator.is_valid(entity=123)


def test_1_type_str_event_data_valid_only():
    validator = BoboValidatorType(types=[str])

    assert validator.is_valid(entity=BoboEventPrimitive(
        event_id="id", timestamp=datetime.now(), data=""))

    assert validator.is_valid(entity=BoboEventPrimitive(
        event_id="id", timestamp=datetime.now(), data="abc"))


def test_1_type_str_event_data_invalid_only():
    validator = BoboValidatorType(types=[str])

    assert not validator.is_valid(entity=BoboEventPrimitive(
        event_id="id", timestamp=datetime.now(), data=None))

    assert not validator.is_valid(entity=BoboEventPrimitive(
        event_id="id", timestamp=datetime.now(), data=123))

    assert not validator.is_valid(entity=BoboEventPrimitive(
        event_id="id", timestamp=datetime.now(), data={"key": 123}))
