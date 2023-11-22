# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Integration tests that ensure complex event generation occurs when expected.
The tests contain typical patterns that may be built by the user with the
pattern builder.

This is not an exhaustive list due to the sheer number of possible
combinations. However, the tests are representative of some of the common
patterns that are likely to frequently occur.
"""

from threading import RLock
from typing import Tuple, Any, List

from bobocep.cep.action import BoboAction, BoboActionHandlerBlocking
from bobocep.cep.event import BoboEventComplex
from bobocep.cep.phenom import BoboPattern, BoboPhenomenon
from bobocep.cep.phenom.pattern.builder import BoboPatternBuilder
from bobocep.setup import BoboSetupSimple


class BoboActionCounter(BoboAction):
    """
    An action that counts how many times it has been executed.
    """

    def __init__(self, name: str):
        """
        :param name: The name of the action.
        """
        super().__init__(name)
        self._lock: RLock = RLock()
        self._counter: int = 0

    def execute(self, event: BoboEventComplex) -> Tuple[bool, Any]:
        """
        Increments the counter value.

        :param event: The complex event.

        :return: True, and the new counter value
        """
        with self._lock:
            self._counter += 1

            return True, None

    @property
    def counter(self) -> int:
        """
        Get counter.
        """
        with self._lock:
            return self._counter


def _setup(patterns: List[BoboPattern]):
    action = BoboActionCounter(name="action")

    phenom = BoboPhenomenon(
        name="phenom",
        patterns=patterns,
        action=action)

    engine = BoboSetupSimple(
        phenomena=[phenom],
        handler=BoboActionHandlerBlocking()
    ).generate()

    return engine, action


class TestValid:

    def test_fb_fb_fb_data_exact(self):
        pattern_1: BoboPattern = BoboPatternBuilder("pattern_1") \
            .followed_by(lambda e, h: int(e.data) == 1) \
            .followed_by(lambda e, h: int(e.data) == 2) \
            .followed_by(lambda e, h: int(e.data) == 3) \
            .generate()

        engine, action = _setup([pattern_1])

        for i in [1, 2, 3]:
            engine.receiver.add_data(i)
            engine.update()

        assert len(engine.decider.all_runs()) == 0
        assert action.counter == 1

    def test_fb_nfb_fb_data_exact(self):
        pattern_1: BoboPattern = BoboPatternBuilder("pattern_1") \
            .followed_by(lambda e, h: int(e.data) == 1) \
            .not_followed_by(lambda e, h: int(e.data) == 2) \
            .followed_by(lambda e, h: int(e.data) == 3) \
            .generate()

        engine, action = _setup([pattern_1])

        for i in [1, 6, 3]:
            engine.receiver.add_data(i)
            engine.update()

        assert len(engine.decider.all_runs()) == 0
        assert action.counter == 1

    def test_fb_nfb_fb_data_not_exact(self):
        pattern_1: BoboPattern = BoboPatternBuilder("pattern_1") \
            .followed_by(lambda e, h: int(e.data) == 1) \
            .not_followed_by(lambda e, h: int(e.data) == 2) \
            .followed_by(lambda e, h: int(e.data) == 3) \
            .generate()

        engine, action = _setup([pattern_1])

        for i in [1, 2, 6, 3]:
            engine.receiver.add_data(i)
            engine.update()

        assert len(engine.decider.all_runs()) == 0
        assert action.counter == 1

    def test_fb_fba_fb_data_exact(self):
        pattern_1: BoboPattern = BoboPatternBuilder("pattern_1") \
            .followed_by(lambda e, h: int(e.data) == 1) \
            .followed_by_any([
                lambda e, h: int(e.data) == 21,
                lambda e, h: int(e.data) == 22,
                lambda e, h: int(e.data) == 23
            ]) \
            .followed_by(lambda e, h: int(e.data) == 3) \
            .generate()

        engine, action = _setup([pattern_1])

        for i in [1, 22, 3]:
            engine.receiver.add_data(i)
            engine.update()

        assert len(engine.decider.all_runs()) == 0
        assert action.counter == 1

    def test_fb_fba_fb_data_not_exact(self):
        pattern_1: BoboPattern = BoboPatternBuilder("pattern_1") \
            .followed_by(lambda e, h: int(e.data) == 1) \
            .followed_by_any([
                lambda e, h: int(e.data) == 21,
                lambda e, h: int(e.data) == 22,
                lambda e, h: int(e.data) == 23
            ]) \
            .followed_by(lambda e, h: int(e.data) == 3) \
            .generate()

        engine, action = _setup([pattern_1])

        for i in [1, 6, 23, 3]:
            engine.receiver.add_data(i)
            engine.update()

        assert len(engine.decider.all_runs()) == 0
        assert action.counter == 1

    def test_fb_nfba_fb_data_exact(self):
        pattern_1: BoboPattern = BoboPatternBuilder("pattern_1") \
            .followed_by(lambda e, h: int(e.data) == 1) \
            .not_followed_by_any([
                lambda e, h: int(e.data) == 21,
                lambda e, h: int(e.data) == 22,
                lambda e, h: int(e.data) == 23
            ]) \
            .followed_by(lambda e, h: int(e.data) == 3) \
            .generate()

        engine, action = _setup([pattern_1])

        for i in [1, 2, 3]:
            engine.receiver.add_data(i)
            engine.update()

        assert len(engine.decider.all_runs()) == 0
        assert action.counter == 1

    def test_fb_nfba_fb_data_not_exact(self):
        pattern_1: BoboPattern = BoboPatternBuilder("pattern_1") \
            .followed_by(lambda e, h: int(e.data) == 1) \
            .not_followed_by_any([
                lambda e, h: int(e.data) == 21,
                lambda e, h: int(e.data) == 22,
                lambda e, h: int(e.data) == 23
            ]) \
            .followed_by(lambda e, h: int(e.data) == 3) \
            .generate()

        engine, action = _setup([pattern_1])

        for i in [1, 21, 22, 23, 2, 3]:
            engine.receiver.add_data(i)
            engine.update()

        assert len(engine.decider.all_runs()) == 0
        assert action.counter == 1

    def test_n_n_n_data_exact(self):
        pattern_1: BoboPattern = BoboPatternBuilder("pattern_1") \
            .next(lambda e, h: int(e.data) == 1) \
            .next(lambda e, h: int(e.data) == 2) \
            .next(lambda e, h: int(e.data) == 3) \
            .generate()

        engine, action = _setup([pattern_1])

        for i in [1, 2, 3]:
            engine.receiver.add_data(i)
            engine.update()

        assert len(engine.decider.all_runs()) == 0
        assert action.counter == 1

    def test_n_nn_n_data_exact(self):
        pattern_1: BoboPattern = BoboPatternBuilder("pattern_1") \
            .next(lambda e, h: int(e.data) == 1) \
            .not_next(lambda e, h: int(e.data) == 2) \
            .next(lambda e, h: int(e.data) == 3) \
            .generate()

        engine, action = _setup([pattern_1])

        for i in [1, 6, 3]:
            engine.receiver.add_data(i)
            engine.update()

        assert len(engine.decider.all_runs()) == 0
        assert action.counter == 1

    def test_fb_fb_fb_pre_data_exact(self):
        pattern_1: BoboPattern = BoboPatternBuilder("pattern_1") \
            .followed_by(lambda e, h: int(e.data) == 1) \
            .followed_by(lambda e, h: int(e.data) == 2) \
            .followed_by(lambda e, h: int(e.data) == 3) \
            .precondition(lambda e, h: int(e.data) > 0) \
            .generate()

        engine, action = _setup([pattern_1])

        for i in [1, 2, 3]:
            engine.receiver.add_data(i)
            engine.update()

        assert len(engine.decider.all_runs()) == 0
        assert action.counter == 1

    def test_fb_fb_fb_halt_data_exact(self):
        pattern_1: BoboPattern = BoboPatternBuilder("pattern_1") \
            .followed_by(lambda e, h: int(e.data) == 1) \
            .followed_by(lambda e, h: int(e.data) == 2) \
            .followed_by(lambda e, h: int(e.data) == 3) \
            .haltcondition(lambda e, h: int(e.data) == 10) \
            .generate()

        engine, action = _setup([pattern_1])

        for i in [1, 2, 3]:
            engine.receiver.add_data(i)
            engine.update()

        assert len(engine.decider.all_runs()) == 0
        assert action.counter == 1

    def test_fb_fb_fb_times_data_exact(self):
        pattern_1: BoboPattern = BoboPatternBuilder("pattern_1") \
            .followed_by(lambda e, h: int(e.data) == 1) \
            .followed_by(lambda e, h: int(e.data) == 2, times=3) \
            .followed_by(lambda e, h: int(e.data) == 3) \
            .generate()

        engine, action = _setup([pattern_1])

        for i in [1, 2, 2, 2, 3]:
            engine.receiver.add_data(i)
            engine.update()

        assert len(engine.decider.all_runs()) == 0
        assert action.counter == 1

    def test_fb_fb_fb_loop_minimum(self):
        pattern_1: BoboPattern = BoboPatternBuilder("pattern_1") \
            .followed_by(lambda e, h: int(e.data) == 1) \
            .followed_by(lambda e, h: int(e.data) == 2, loop=True) \
            .followed_by(lambda e, h: int(e.data) == 3) \
            .generate()

        engine, action = _setup([pattern_1])

        for i in [1, 3]:
            engine.receiver.add_data(i)
            engine.update()

        assert len(engine.decider.all_runs()) == 0
        assert action.counter == 1

    def test_fb_fb_fb_loop_once(self):
        pattern_1: BoboPattern = BoboPatternBuilder("pattern_1") \
            .followed_by(lambda e, h: int(e.data) == 1) \
            .followed_by(lambda e, h: int(e.data) == 2, loop=True) \
            .followed_by(lambda e, h: int(e.data) == 3) \
            .generate()

        engine, action = _setup([pattern_1])

        for i in [1, 2, 3]:
            engine.receiver.add_data(i)
            engine.update()

        assert len(engine.decider.all_runs()) == 0
        assert action.counter == 1

    def test_fb_fb_fb_loop_many(self):
        pattern_1: BoboPattern = BoboPatternBuilder("pattern_1") \
            .followed_by(lambda e, h: int(e.data) == 1) \
            .followed_by(lambda e, h: int(e.data) == 2, loop=True) \
            .followed_by(lambda e, h: int(e.data) == 3) \
            .generate()

        engine, action = _setup([pattern_1])

        for i in [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3]:
            engine.receiver.add_data(i)
            engine.update()

        assert len(engine.decider.all_runs()) == 0
        assert action.counter == 1

    def test_fb_fb_fb_optional_included(self):
        pattern_1: BoboPattern = BoboPatternBuilder("pattern_1") \
            .followed_by(lambda e, h: int(e.data) == 1) \
            .followed_by(lambda e, h: int(e.data) == 2, optional=True) \
            .followed_by(lambda e, h: int(e.data) == 3) \
            .generate()

        engine, action = _setup([pattern_1])

        for i in [1, 2, 3]:
            engine.receiver.add_data(i)
            engine.update()

        assert len(engine.decider.all_runs()) == 0
        assert action.counter == 1

    def test_fb_fb_fb_optional_not_included(self):
        pattern_1: BoboPattern = BoboPatternBuilder("pattern_1") \
            .followed_by(lambda e, h: int(e.data) == 1) \
            .followed_by(lambda e, h: int(e.data) == 2, optional=True) \
            .followed_by(lambda e, h: int(e.data) == 3) \
            .generate()

        engine, action = _setup([pattern_1])

        for i in [1, 3]:
            engine.receiver.add_data(i)
            engine.update()

        assert len(engine.decider.all_runs()) == 0
        assert action.counter == 1


class TestInvalid:

    def test_fb_fb_fb_pre(self):
        pattern_1: BoboPattern = BoboPatternBuilder("pattern_1") \
            .followed_by(lambda e, h: int(e.data) == 1) \
            .followed_by(lambda e, h: int(e.data) == 2) \
            .followed_by(lambda e, h: int(e.data) == 3) \
            .precondition(lambda e, h: int(e.data) > 0) \
            .generate()

        engine, action = _setup([pattern_1])

        for i in [1, 0, 2, 3]:
            engine.receiver.add_data(i)
            engine.update()

        assert len(engine.decider.all_runs()) == 0
        assert action.counter == 0

    def test_fb_fb_fb_halt(self):
        pattern_1: BoboPattern = BoboPatternBuilder("pattern_1") \
            .followed_by(lambda e, h: int(e.data) == 1) \
            .followed_by(lambda e, h: int(e.data) == 2) \
            .followed_by(lambda e, h: int(e.data) == 3) \
            .haltcondition(lambda e, h: int(e.data) == 10) \
            .generate()

        engine, action = _setup([pattern_1])

        for i in [1, 10, 2, 3]:
            engine.receiver.add_data(i)
            engine.update()

        assert len(engine.decider.all_runs()) == 0
        assert action.counter == 0

    def test_n_n_n(self):
        pattern_1: BoboPattern = BoboPatternBuilder("pattern_1") \
            .next(lambda e, h: int(e.data) == 1) \
            .next(lambda e, h: int(e.data) == 2) \
            .next(lambda e, h: int(e.data) == 3) \
            .generate()

        engine, action = _setup([pattern_1])

        for i in [1, 6, 3]:
            engine.receiver.add_data(i)
            engine.update()

        assert len(engine.decider.all_runs()) == 0
        assert action.counter == 0

    def test_n_nn_n(self):
        pattern_1: BoboPattern = BoboPatternBuilder("pattern_1") \
            .next(lambda e, h: int(e.data) == 1) \
            .not_next(lambda e, h: int(e.data) == 2) \
            .next(lambda e, h: int(e.data) == 3) \
            .generate()

        engine, action = _setup([pattern_1])

        for i in [1, 2, 3]:
            engine.receiver.add_data(i)
            engine.update()

        assert len(engine.decider.all_runs()) == 0
        assert action.counter == 0
