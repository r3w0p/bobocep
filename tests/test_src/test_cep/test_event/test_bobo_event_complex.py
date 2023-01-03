# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import pytest

from src.cep.event.bobo_event_complex import BoboEventComplex
from src.cep.event.bobo_event_error import BoboEventError
from src.cep.event.bobo_history import BoboHistory
from src.cep.event.timestamp_gen.bobo_timestamp_gen_epoch import \
    BoboTimestampGenEpoch


class TestValid:
    """"""


class TestInvalid:

    def test_event_id_length_0(self):
        with pytest.raises(BoboEventError):
            BoboEventComplex(
                event_id="",
                timestamp=BoboTimestampGenEpoch().generate(),
                data=None,
                process_name="process",
                pattern_name="pattern",
                history=BoboHistory(events={}))

    def test_process_name_length_0(self):
        with pytest.raises(BoboEventError):
            BoboEventComplex(
                event_id="event_id_gen",
                timestamp=BoboTimestampGenEpoch().generate(),
                data=None,
                process_name="",
                pattern_name="pattern",
                history=BoboHistory(events={}))

    def test_pattern_name_length_0(self):
        with pytest.raises(BoboEventError):
            BoboEventComplex(
                event_id="event_id_gen",
                timestamp=BoboTimestampGenEpoch().generate(),
                data=None,
                process_name="process",
                pattern_name="",
                history=BoboHistory(events={}))
