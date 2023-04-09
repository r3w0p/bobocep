# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
import pytest

from bobocep.cep.engine.decider.runserial import BoboRunSerial, BoboRunSerialError
from bobocep.cep.event import BoboHistory
from tests.test_bobocep.test_cep.test_engine.test_decider import tc_run_tuple
from tests.test_bobocep.test_cep.test_event import tc_event_simple


class TestValid:

    def test_properties(self):
        runserial = BoboRunSerial(
            run_id="run_id",
            phenomenon_name="phenomenon_name",
            pattern_name="pattern_name",
            block_index=1,
            history=BoboHistory({"pattern_group": [tc_event_simple(
                event_id="event_id"
            )]})
        )

        assert runserial.run_id == "run_id"
        assert runserial.phenomenon_name == "phenomenon_name"
        assert runserial.pattern_name == "pattern_name"
        assert runserial.block_index == 1
        assert runserial.history.size() == 1
        assert runserial.history.all_groups()[0] == "pattern_group"
        assert runserial.history.all_events()[0].event_id == "event_id"

    def test_to_json_str_to_instance(self):
        run_id = "run_id"
        phenomenon_name = "phenomenon_name"
        pattern_name = "pattern_name"
        block_index = 1

        pattern_group = "pattern_group"
        event_id = "event_id"
        history = BoboHistory({pattern_group: [tc_event_simple(
            event_id=event_id
        )]})

        rs = BoboRunSerial(
            run_id=run_id,
            phenomenon_name=phenomenon_name,
            pattern_name=pattern_name,
            block_index=block_index,
            history=history
        )

        rs_tojsonstr = rs.to_json_str()
        rs_fromstr = BoboRunSerial.from_json_str(rs_tojsonstr)

        assert rs_fromstr.run_id == rs.run_id
        assert rs_fromstr.phenomenon_name == rs.phenomenon_name
        assert rs_fromstr.pattern_name == rs.pattern_name
        assert rs_fromstr.block_index == rs.block_index

        h_groups = rs_fromstr.history.all_groups()
        assert len(h_groups) == 1
        assert h_groups[0] == pattern_group

        h_events = rs_fromstr.history.all_events()
        assert len(h_events) == 1
        assert h_events[0].event_id == event_id

    def test_to_str_to_instance(self):
        run_id = "run_id"
        phenomenon_name = "phenomenon_name"
        pattern_name = "pattern_name"
        block_index = 1

        pattern_group = "pattern_group"
        event_id = "event_id"
        history = BoboHistory({pattern_group: [tc_event_simple(
            event_id=event_id
        )]})

        rs = BoboRunSerial(
            run_id=run_id,
            phenomenon_name=phenomenon_name,
            pattern_name=pattern_name,
            block_index=block_index,
            history=history
        )

        rs_tostr = rs.__str__()
        rs_fromstr = BoboRunSerial.from_json_str(rs_tostr)

        assert rs_fromstr.run_id == rs.run_id
        assert rs_fromstr.phenomenon_name == rs.phenomenon_name
        assert rs_fromstr.pattern_name == rs.pattern_name
        assert rs_fromstr.block_index == rs.block_index

        h_groups = rs_fromstr.history.all_groups()
        assert len(h_groups) == 1
        assert h_groups[0] == pattern_group

        h_events = rs_fromstr.history.all_events()
        assert len(h_events) == 1
        assert h_events[0].event_id == event_id


class TestInvalid:

    def test_length_0_run_id(self):
        with pytest.raises(BoboRunSerialError):
            tc_run_tuple(run_id="")

    def test_length_0_phenomenon_name(self):
        with pytest.raises(BoboRunSerialError):
            tc_run_tuple(phenomenon_name="")

    def test_block_index_zero(self):
        with pytest.raises(BoboRunSerialError):
            tc_run_tuple(block_index=0)

    def test_block_index_negative(self):
        with pytest.raises(BoboRunSerialError):
            tc_run_tuple(block_index=-1)

    def test_history_no_events(self):
        with pytest.raises(BoboRunSerialError):
            tc_run_tuple(history=BoboHistory({}))
