# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import tests.common as tc
from bobocep.cep.engine.task.receiver.validator import BoboValidatorJSONable


class TestValid:

    def test_none(self):
        assert BoboValidatorJSONable().is_valid(None)

    def test_int(self):
        assert BoboValidatorJSONable().is_valid(123)

    def test_float(self):
        assert BoboValidatorJSONable().is_valid(123.456)

    def test_str_empty(self):
        assert BoboValidatorJSONable().is_valid("")

    def test_str(self):
        assert BoboValidatorJSONable().is_valid("string")

    def test_bool_true(self):
        assert BoboValidatorJSONable().is_valid(True)

    def test_bool_false(self):
        assert BoboValidatorJSONable().is_valid(False)

    def test_list_empty(self):
        assert BoboValidatorJSONable().is_valid([])

    def test_list_ints(self):
        assert BoboValidatorJSONable().is_valid([123, 456, 789])

    def test_list_strings(self):
        assert BoboValidatorJSONable().is_valid(["abc", "def", "ghi"])

    def test_dict_empty(self):
        assert BoboValidatorJSONable().is_valid({})

    def test_dict_key_str_val_int(self):
        assert BoboValidatorJSONable().is_valid({"abc": 123})

    def test_event_simple(self):
        assert BoboValidatorJSONable().is_valid(tc.event_simple())

    def test_event_complex(self):
        assert BoboValidatorJSONable().is_valid(tc.event_complex())

    def test_event_action(self):
        assert BoboValidatorJSONable().is_valid(tc.event_action())


class TestInvalid:

    # "If check_circular is false (default: True), then the circular
    # reference check for container types will be skipped and a circular
    # reference will result in a RecursionError (or worse)."

    # "If skipkeys is true (default: False), then dict keys that are not of a
    # basic type (str, int, float, bool, None) will be skipped instead of
    # raising a TypeError."

    # "If specified, default should be a function that gets called for
    # objects that can’t otherwise be serialized. It should return a JSON
    # encodable version of the object or raise a TypeError. If not specified,
    # TypeError is raised."

    # "If allow_nan is false (default: True), then it will be a ValueError
    # to serialize out of range float values (nan, inf, -inf) in strict
    # compliance of the JSON specification. If allow_nan is true, their
    # JavaScript equivalents (NaN, Infinity, -Infinity) will be used."

    def test_bytes(self):
        assert not BoboValidatorJSONable().is_valid("abc".encode("utf-8"))
