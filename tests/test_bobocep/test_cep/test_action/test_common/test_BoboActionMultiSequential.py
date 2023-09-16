# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

from bobocep.cep.action import BoboActionError
from bobocep.cep.action.common.multi import BoboActionMultiSequential
from tests.test_bobocep.test_cep.test_action import BoboActionTrue, \
    BoboActionFalse
from tests.test_bobocep.test_cep.test_event import tc_event_complex


class TestValid:

    def test_3_actions_all_success_stop(self):
        actions = [
            BoboActionTrue(),
            BoboActionTrue(),
            BoboActionTrue()
        ]
        multi = BoboActionMultiSequential(
            name="test_multi",
            actions=actions,
            stop_on_fail=True)

        success, data = multi.execute(tc_event_complex())

        assert success
        assert len(data) == len(actions)

        a1_success, a1_data = data[0]
        a2_success, a2_data = data[1]
        a3_success, a3_data = data[2]

        assert a1_success
        assert a2_success
        assert a3_success

    def test_3_actions_middle_fail_stop(self):
        actions = [
            BoboActionTrue(),
            BoboActionFalse(),
            BoboActionTrue()
        ]
        multi = BoboActionMultiSequential(
            name="test_multi",
            actions=actions,
            stop_on_fail=True)

        success, data = multi.execute(tc_event_complex())

        assert not success
        assert len(data) == (len(actions) - 1)

        a1_success, a1_data = data[0]
        a2_success, a2_data = data[1]

        assert a1_success
        assert not a2_success

    def test_3_actions_middle_fail_no_stop(self):
        actions = [
            BoboActionTrue(),
            BoboActionFalse(),
            BoboActionTrue()
        ]
        multi = BoboActionMultiSequential(
            name="test_multi",
            actions=actions,
            stop_on_fail=False)

        success, data = multi.execute(tc_event_complex())

        assert not success
        assert len(data) == len(actions)

        a1_success, a1_data = data[0]
        a2_success, a2_data = data[1]
        a3_success, a3_data = data[2]

        assert a1_success
        assert not a2_success
        assert a3_success


class TestInvalid:

    def test_0_actions(self):
        with pytest.raises(BoboActionError):
            BoboActionMultiSequential(
                name="test_multi",
                actions=[],
                stop_on_fail=True)
