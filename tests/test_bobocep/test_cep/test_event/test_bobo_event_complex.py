# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from datetime import datetime

import pytest

from bobocep.cep.event.bobo_event_complex import BoboEventComplex
from bobocep.cep.event.bobo_event_error import BoboEventError
from bobocep.cep.event.bobo_history import BoboHistory


class TestValid:
    """"""


class TestInvalid:

    def test_event_id_length_0(self):
        with pytest.raises(BoboEventError):
            BoboEventComplex(
                event_id="",
                timestamp=datetime.now(),
                data=None,
                process_name="process",
                pattern_name="pattern",
                history=BoboHistory(events={}))

    def test_process_name_length_0(self):
        with pytest.raises(BoboEventError):
            BoboEventComplex(
                event_id="event_id_gen",
                timestamp=datetime.now(),
                data=None,
                process_name="",
                pattern_name="pattern",
                history=BoboHistory(events={}))

    def test_pattern_name_length_0(self):
        with pytest.raises(BoboEventError):
            BoboEventComplex(
                event_id="event_id_gen",
                timestamp=datetime.now(),
                data=None,
                process_name="process",
                pattern_name="",
                history=BoboHistory(events={}))
