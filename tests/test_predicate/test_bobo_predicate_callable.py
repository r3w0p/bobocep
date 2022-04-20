# Copyright (c) The BoboCEP Authors
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License v3.0.

from datetime import datetime

from bobocep.events.bobo_event_primitive import BoboEventPrimitive
from bobocep.events.bobo_history import BoboHistory
from bobocep.predicate.bobo_predicate_callable import \
    BoboPredicateCallable


def test_evaluate_return_true_if_int_value_greater_than():
    predicate = BoboPredicateCallable(call=lambda e, h: e.data > 10)

    event_1 = BoboEventPrimitive(
        event_id="id_1", timestamp=datetime.now(), data=20)

    event_2 = BoboEventPrimitive(
        event_id="id_2", timestamp=datetime.now(), data=5)

    history = BoboHistory(events={})

    assert predicate.evaluate(event=event_1, history=history)
    assert not predicate.evaluate(event=event_2, history=history)
