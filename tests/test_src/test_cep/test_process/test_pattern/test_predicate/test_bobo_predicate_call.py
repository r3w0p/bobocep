# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

from src.cep.event.bobo_event_simple import BoboEventSimple
from src.cep.event.bobo_history import BoboHistory
from src.cep.event.timestamp_gen.bobo_timestamp_gen_epoch import \
    BoboTimestampGenEpoch
from src.cep.process.pattern.predicate.bobo_predicate_call import \
    BoboPredicateCall
from src.cep.process.pattern.predicate.bobo_predicate_error import \
    BoboPredicateError


class TestValid:

    def test_evaluate_correct_return_value(self):
        predicate = BoboPredicateCall(call=lambda e, h: e.data)

        event_1 = BoboEventSimple(
            event_id="1", timestamp=BoboTimestampGenEpoch().generate(),
            data=True)

        event_2 = BoboEventSimple(
            event_id="2", timestamp=BoboTimestampGenEpoch().generate(),
            data=False)

        history = BoboHistory(events={})

        assert predicate.evaluate(event=event_1, history=history)
        assert not predicate.evaluate(event=event_2, history=history)


class TestInvalid:

    def test_callable_too_few_parameters(self):
        with pytest.raises(BoboPredicateError):
            BoboPredicateCall(call=lambda a: True)

    def test_callable_too_many_parameters(self):
        with pytest.raises(BoboPredicateError):
            BoboPredicateCall(call=lambda a, b, c, d, e: True)
