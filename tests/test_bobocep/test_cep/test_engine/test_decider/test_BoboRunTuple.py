# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
import pytest

from bobocep.cep.engine.decider.runtup import BoboRunTuple, BoboRunTupleError
from bobocep.cep.event import BoboHistory
from tests.test_bobocep.test_cep.test_engine.test_decider import tc_run_tuple
from tests.test_bobocep.test_cep.test_event import tc_event_simple


class TestValid:

    def test_properties(self):
        runtup = BoboRunTuple(
            run_id="run_id",
            phenomenon_name="phenomenon_name",
            pattern_name="pattern_name",
            block_index=1,
            history=BoboHistory({"pattern_group": [tc_event_simple(
                event_id="event_id"
            )]})
        )

        assert runtup.run_id == "run_id"
        assert runtup.phenomenon_name == "phenomenon_name"
        assert runtup.pattern_name == "pattern_name"
        assert runtup.block_index == 1
        assert runtup.history.size() == 1
        assert runtup.history.all_groups()[0] == "pattern_group"
        assert runtup.history.all_events()[0].event_id == "event_id"


class TestInvalid:

    def test_length_0_run_id(self):
        with pytest.raises(BoboRunTupleError):
            tc_run_tuple(run_id="")

    def test_length_0_phenomenon_name(self):
        with pytest.raises(BoboRunTupleError):
            tc_run_tuple(phenomenon_name="")

    def test_block_index_zero(self):
        with pytest.raises(BoboRunTupleError):
            tc_run_tuple(block_index=0)

    def test_block_index_negative(self):
        with pytest.raises(BoboRunTupleError):
            tc_run_tuple(block_index=-1)

    def test_history_no_events(self):
        with pytest.raises(BoboRunTupleError):
            tc_run_tuple(history=BoboHistory({}))
