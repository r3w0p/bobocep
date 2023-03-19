# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from threading import Thread
from time import sleep

import pytest
import tests.common as tc
from bobocep.cep.engine import BoboEngine, BoboEngineError
from bobocep.cep.engine.decider import BoboRunTuple, BoboDecider
from bobocep.cep.engine.forwarder import BoboForwarder
from bobocep.cep.engine.producer import BoboProducer
from bobocep.cep.engine.receiver import BoboReceiver
from bobocep.cep.event import BoboEventSimple, BoboEventComplex, \
    BoboEventAction


def run_engine(engine: BoboEngine):
    engine.run()


class TestValid:

    def test_property_receiver(self):
        engine, _, _, _, _ = tc.engine_subs([tc.phenomenon()])
        assert isinstance(engine.receiver, BoboReceiver)

    def test_property_decider(self):
        engine, _, _, _, _ = tc.engine_subs([tc.phenomenon()])
        assert isinstance(engine.decider, BoboDecider)

    def test_property_producer(self):
        engine, _, _, _, _ = tc.engine_subs([tc.phenomenon()])
        assert isinstance(engine.producer, BoboProducer)

    def test_property_forwarder(self):
        engine, _, _, _, _ = tc.engine_subs([tc.phenomenon()])
        assert isinstance(engine.forwarder, BoboForwarder)

    def test_1_pattern_with_action_all_data_at_once(self):
        phenomena = [tc.phenomenon(
            name="phenomenon_a",
            datagen=lambda p, h: True,
            patterns=[
                tc.pattern("pattern_123", data_blocks=[1, 2, 3])
            ],
            action=tc.BoboActionTrue("action_true")
        )]
        engine, rec_sub, dec_sub, pro_sub, fwd_sub = tc.engine_subs(phenomena)

        engine.receiver.add_data(1)
        engine.receiver.add_data(2)
        engine.receiver.add_data(3)
        assert engine.receiver.size() == 3

        assert engine.update()

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
        assert len(dec_sub.completed) == 1
        assert dec_sub.completed[0].phenomenon_name == "phenomenon_a"
        assert dec_sub.completed[0].pattern_name == "pattern_123"
        dec_history = dec_sub.completed[0].history
        assert dec_history.group("g1")[0].data == 1
        assert dec_history.group("g2")[0].data == 2
        assert dec_history.group("g3")[0].data == 3

        # Producer output: complex event
        assert len(pro_sub.output) == 1
        assert isinstance(pro_sub.output[0], BoboEventComplex)
        assert pro_sub.output[0].data is True
        assert pro_sub.output[0].phenomenon_name == "phenomenon_a"
        assert pro_sub.output[0].pattern_name == "pattern_123"
        assert pro_sub.output[0].history.all() == dec_history.all()

        # Forwarder output: action event
        assert len(fwd_sub.output) == 1
        assert isinstance(fwd_sub.output[0], BoboEventAction)
        assert fwd_sub.output[0].data is True
        assert fwd_sub.output[0].phenomenon_name == "phenomenon_a"
        assert fwd_sub.output[0].pattern_name == "pattern_123"
        assert fwd_sub.output[0].action_name == "action_true"
        assert fwd_sub.output[0].success is True

    def test_1_pattern_with_action_one_at_a_time(self):
        phenomena = [tc.phenomenon(
            name="phenomenon_a",
            datagen=lambda p, h: True,
            patterns=[
                tc.pattern("pattern_123", data_blocks=[1, 2, 3])
            ],
            action=tc.BoboActionTrue("action_true")
        )]
        engine, rec_sub, dec_sub, pro_sub, fwd_sub = tc.engine_subs(
            phenomena,
            times_receiver=1,
            times_decider=1,
            times_producer=1,
            times_forwarder=1
        )

        engine.receiver.add_data(1)
        engine.receiver.add_data(2)
        engine.receiver.add_data(3)
        assert engine.receiver.size() == 3

        # Update 1
        assert engine.update()

        # Receiver output: one simple event
        assert len(rec_sub.output) == 1
        assert isinstance(rec_sub.output[0], BoboEventSimple)
        assert rec_sub.output[0].data == 1
        assert engine.receiver.size() == 2

        # Other output: nothing
        assert len(dec_sub.completed) == 0
        assert len(pro_sub.output) == 0
        assert len(fwd_sub.output) == 0

        # Update 2
        assert engine.update()

        # Receiver output: two simple events
        assert len(rec_sub.output) == 2
        assert isinstance(rec_sub.output[1], BoboEventSimple)
        assert rec_sub.output[1].data == 2
        assert engine.receiver.size() == 1

        # Other output: nothing
        assert len(dec_sub.completed) == 0
        assert len(pro_sub.output) == 0
        assert len(fwd_sub.output) == 0

        # Update 3
        assert engine.update()

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
        assert len(dec_sub.completed) == 1
        assert isinstance(dec_sub.completed[0], BoboRunTuple)
        assert dec_sub.completed[0].phenomenon_name == "phenomenon_a"
        assert dec_sub.completed[0].pattern_name == "pattern_123"
        dec_history = dec_sub.completed[0].history
        assert dec_history.group("g1")[0].data == 1
        assert dec_history.group("g2")[0].data == 2
        assert dec_history.group("g3")[0].data == 3

        # Producer output: complex event
        assert len(pro_sub.output) == 1
        assert isinstance(pro_sub.output[0], BoboEventComplex)
        assert pro_sub.output[0].data is True
        assert pro_sub.output[0].phenomenon_name == "phenomenon_a"
        assert pro_sub.output[0].pattern_name == "pattern_123"
        assert pro_sub.output[0].history.all() == dec_history.all()

        # Forwarder output: action event
        assert len(fwd_sub.output) == 1
        assert isinstance(fwd_sub.output[0], BoboEventAction)
        assert fwd_sub.output[0].data is True
        assert fwd_sub.output[0].phenomenon_name == "phenomenon_a"
        assert fwd_sub.output[0].pattern_name == "pattern_123"
        assert fwd_sub.output[0].action_name == "action_true"
        assert fwd_sub.output[0].success is True

    def test_close_then_update(self):
        phenomena = [tc.phenomenon()]
        engine, rec_sub, dec_sub, pro_sub, fwd_sub = tc.engine_subs(phenomena)

        engine.close()
        assert engine.is_closed()
        assert engine.update() is False

    def test_close_then_run(self):
        phenomena = [tc.phenomenon()]
        engine, rec_sub, dec_sub, pro_sub, fwd_sub = tc.engine_subs(phenomena)

        engine.close()
        assert engine.is_closed()
        assert engine.run() is None

    def test_run_then_close(self):
        phenomena = [tc.phenomenon()]
        engine, rec_sub, dec_sub, pro_sub, fwd_sub = tc.engine_subs(phenomena)

        t = Thread(target=run_engine, args=[engine])
        t.start()
        engine.close()
        t.join()

        assert engine.is_closed()

    def test_run_then_complete_pattern_then_close(self):
        phenomena = [tc.phenomenon(
            name="phenom_a",
            datagen=lambda p, h: True,
            patterns=[
                tc.pattern("pattern_123", data_blocks=[1, 2, 3])
            ],
            action=tc.BoboActionTrue("action_true")
        )]
        engine, rec_sub, dec_sub, pro_sub, fwd_sub = tc.engine_subs(phenomena)

        t = Thread(target=run_engine, args=[engine])
        t.start()

        engine.receiver.add_data(1)
        engine.receiver.add_data(2)
        engine.receiver.add_data(3)
        sleep(1)
        engine.close()
        t.join()

        assert engine.is_closed()
        # 1 complex + 1 action event from forwarder passed to decider
        assert engine.receiver.size() == 0

        # Receiver outputs 5 events: 3 simple + 1 complex + 1 action
        assert len(rec_sub.output) == 5
        assert len(dec_sub.completed) == 1
        assert len(pro_sub.output) == 1
        assert len(fwd_sub.output) == 1


class TestInvalid:

    def test_times_receiver_negative(self):
        with pytest.raises(BoboEngineError):
            tc.engine_subs([tc.phenomenon()], times_receiver=-1)

    def test_times_decider_negative(self):
        with pytest.raises(BoboEngineError):
            tc.engine_subs([tc.phenomenon()], times_decider=-1)

    def test_times_producer_negative(self):
        with pytest.raises(BoboEngineError):
            tc.engine_subs([tc.phenomenon()], times_producer=-1)

    def test_times_forwarder_negative(self):
        with pytest.raises(BoboEngineError):
            tc.engine_subs([tc.phenomenon()], times_forwarder=-1)
