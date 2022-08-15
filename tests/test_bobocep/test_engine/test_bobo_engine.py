# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
import pytest

import tests.common as tc
from bobocep.engine.bobo_engine_error import BoboEngineError
from bobocep.event.bobo_event_action import BoboEventAction
from bobocep.event.bobo_event_complex import BoboEventComplex
from bobocep.event.bobo_event_simple import BoboEventSimple


class TestValid:

    def test_1_pattern_with_action_all_data_at_once(self):
        processes = [tc.process(
            name="process_a",
            datagen=lambda p, h: True,
            patterns=[
                tc.pattern("pattern_123", data_blocks=[1, 2, 3])
            ],
            action=tc.BoboActionTrue("action_true")
        )]
        engine, rec_sub, dec_sub, pro_sub, fwd_sub = tc.engine_subs(processes)

        engine.receiver.add_data(1)
        engine.receiver.add_data(2)
        engine.receiver.add_data(3)
        assert engine.receiver.size() == 3

        engine.update()

        # Receiver output: data wrapped in simple events
        assert len(rec_sub.output) == 3
        assert all(isinstance(rec_sub.output[i], BoboEventSimple)
                   for i in range(3))
        assert rec_sub.output[0].data == 1
        assert rec_sub.output[1].data == 2
        assert rec_sub.output[2].data == 3
        # Complex event and action event passed to receiver
        assert engine.receiver.size() == 2

        # Decider output: full history of events that caused run to complete
        assert len(dec_sub.output) == 1
        assert isinstance(dec_sub.output[0], tuple)
        assert dec_sub.output[0][0] == "process_a"
        assert dec_sub.output[0][1] == "pattern_123"
        dec_history = dec_sub.output[0][2]
        assert dec_history.group("g1")[0].data == 1
        assert dec_history.group("g2")[0].data == 2
        assert dec_history.group("g3")[0].data == 3

        # Producer output: complex event
        assert len(pro_sub.output) == 1
        assert isinstance(pro_sub.output[0], BoboEventComplex)
        assert pro_sub.output[0].data is True
        assert pro_sub.output[0].process_name == "process_a"
        assert pro_sub.output[0].pattern_name == "pattern_123"
        assert pro_sub.output[0].history.all() == dec_history.all()

        # Forwarder output: action event
        assert len(fwd_sub.output) == 1
        assert isinstance(fwd_sub.output[0], BoboEventAction)
        assert fwd_sub.output[0].data is True
        assert fwd_sub.output[0].process_name == "process_a"
        assert fwd_sub.output[0].pattern_name == "pattern_123"
        assert fwd_sub.output[0].action_name == "action_true"
        assert fwd_sub.output[0].success is True

    def test_1_pattern_with_action_one_at_a_time(self):
        processes = [tc.process(
            name="process_a",
            datagen=lambda p, h: True,
            patterns=[
                tc.pattern("pattern_123", data_blocks=[1, 2, 3])
            ],
            action=tc.BoboActionTrue("action_true")
        )]
        engine, rec_sub, dec_sub, pro_sub, fwd_sub = tc.engine_subs(processes)

        engine.receiver.add_data(1)
        engine.receiver.add_data(2)
        engine.receiver.add_data(3)
        assert engine.receiver.size() == 3

        # Update 1
        engine.update(1, 1, 1, 1)

        # Receiver output: one simple event
        assert len(rec_sub.output) == 1
        assert isinstance(rec_sub.output[0], BoboEventSimple)
        assert rec_sub.output[0].data == 1
        assert engine.receiver.size() == 2

        # Other output: nothing
        assert len(dec_sub.output) == 0
        assert len(pro_sub.output) == 0
        assert len(fwd_sub.output) == 0

        # Update 2
        engine.update(1, 1, 1, 1)

        # Receiver output: two simple events
        assert len(rec_sub.output) == 2
        assert isinstance(rec_sub.output[1], BoboEventSimple)
        assert rec_sub.output[1].data == 2
        assert engine.receiver.size() == 1

        # Other output: nothing
        assert len(dec_sub.output) == 0
        assert len(pro_sub.output) == 0
        assert len(fwd_sub.output) == 0

        # Update 3
        engine.update(1, 1, 1, 1)

        # Receiver output: data wrapped in simple events
        assert len(rec_sub.output) == 3
        assert all(isinstance(rec_sub.output[i], BoboEventSimple)
                   for i in range(3))
        assert rec_sub.output[0].data == 1
        assert rec_sub.output[1].data == 2
        assert rec_sub.output[2].data == 3
        # Complex event and action event passed to receiver
        assert engine.receiver.size() == 2

        # Decider output: full history of events that caused run to complete
        assert len(dec_sub.output) == 1
        assert isinstance(dec_sub.output[0], tuple)
        assert dec_sub.output[0][0] == "process_a"
        assert dec_sub.output[0][1] == "pattern_123"
        dec_history = dec_sub.output[0][2]
        assert dec_history.group("g1")[0].data == 1
        assert dec_history.group("g2")[0].data == 2
        assert dec_history.group("g3")[0].data == 3

        # Producer output: complex event
        assert len(pro_sub.output) == 1
        assert isinstance(pro_sub.output[0], BoboEventComplex)
        assert pro_sub.output[0].data is True
        assert pro_sub.output[0].process_name == "process_a"
        assert pro_sub.output[0].pattern_name == "pattern_123"
        assert pro_sub.output[0].history.all() == dec_history.all()

        # Forwarder output: action event
        assert len(fwd_sub.output) == 1
        assert isinstance(fwd_sub.output[0], BoboEventAction)
        assert fwd_sub.output[0].data is True
        assert fwd_sub.output[0].process_name == "process_a"
        assert fwd_sub.output[0].pattern_name == "pattern_123"
        assert fwd_sub.output[0].action_name == "action_true"
        assert fwd_sub.output[0].success is True


class TestInvalid:

    def test_times_receiver_negative(self):
        processes = [tc.process()]
        engine, rec_sub, dec_sub, pro_sub, fwd_sub = tc.engine_subs(processes)

        with pytest.raises(BoboEngineError):
            engine.update(times_receiver=-1)

    def test_times_decider_negative(self):
        processes = [tc.process()]
        engine, rec_sub, dec_sub, pro_sub, fwd_sub = tc.engine_subs(processes)

        with pytest.raises(BoboEngineError):
            engine.update(times_decider=-1)

    def test_times_producer_negative(self):
        processes = [tc.process()]
        engine, rec_sub, dec_sub, pro_sub, fwd_sub = tc.engine_subs(processes)

        with pytest.raises(BoboEngineError):
            engine.update(times_producer=-1)

    def test_times_forwarder_negative(self):
        processes = [tc.process()]
        engine, rec_sub, dec_sub, pro_sub, fwd_sub = tc.engine_subs(processes)

        with pytest.raises(BoboEngineError):
            engine.update(times_forwarder=-1)
