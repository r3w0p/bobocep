# Copyright (c) 2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from datetime import datetime
from typing import Callable, List, Any

from bobocep.action.bobo_action import BoboAction
from bobocep.event.bobo_event_action import BoboEventAction
from bobocep.event.bobo_event_complex import BoboEventComplex
from bobocep.event.bobo_event_simple import BoboEventSimple
from bobocep.event.bobo_history import BoboHistory
from bobocep.event.event_id.bobo_event_id import BoboEventID
from bobocep.event.event_id.bobo_event_id_unique import BoboEventIDUnique
from bobocep.process.bobo_process import BoboProcess
from bobocep.process.pattern.bobo_pattern import BoboPattern
from bobocep.process.pattern.bobo_pattern_block import BoboPatternBlock
from bobocep.process.pattern.predicate.bobo_predicate import BoboPredicate
from bobocep.process.pattern.predicate.bobo_predicate_call import \
    BoboPredicateCall


class BoboActionTrue(BoboAction):
    """An action that is always successful."""

    def __init__(self, name: str = "action"):
        super().__init__(name)

    def execute(self, event: BoboEventComplex) -> BoboEventAction:
        return BoboEventAction(
            event_id=BoboEventIDUnique().generate(),
            timestamp=datetime.now(),
            data=True,
            process_name=event.process_name,
            pattern_name=event.pattern_name,
            action_name=self.name,
            success=True)


class BoboActionFalse(BoboAction):
    """An action that is always unsuccessful."""

    def __init__(self, name: str = "action"):
        super().__init__(name)

    def execute(self, event: BoboEventComplex) -> BoboEventAction:
        return BoboEventAction(
            event_id=BoboEventIDUnique().generate(),
            timestamp=datetime.now(),
            data=False,
            process_name=event.process_name,
            pattern_name=event.pattern_name,
            action_name=self.name,
            success=False)


class BoboEventIDSameEveryTime(BoboEventID):
    """Produces the same ID string every time. Useful for testing whether
       an exception is raised on the presence of duplicate IDs."""

    def __init__(self, id_str: str = "id_str"):
        super().__init__()

        self.id_str = id_str

    def generate(self) -> str:
        return self.id_str


def event_simple(event_id: str = None,
                 timestamp: datetime = None,
                 data=None):
    return BoboEventSimple(
        event_id=event_id if event_id is not None else
        BoboEventIDUnique().generate(),
        timestamp=timestamp if timestamp is not None else
        datetime.now(),
        data=data)


def event_complex(event_id: str = None,
                  timestamp: datetime = None,
                  data=None,
                  process_name: str = "process",
                  pattern_name: str = "pattern",
                  history: BoboHistory = None):
    return BoboEventComplex(
        event_id=event_id if event_id is not None else
        BoboEventIDUnique().generate(),
        timestamp=timestamp if timestamp is not None else
        datetime.now(),
        data=data,
        process_name=process_name,
        pattern_name=pattern_name,
        history=history if history is not None else
        BoboHistory(events={}))


def event_action(event_id: str = None,
                 timestamp: datetime = None,
                 data=None,
                 process_name: str = "process",
                 pattern_name: str = "pattern",
                 action_name: str = "action",
                 success: bool = True):
    return BoboEventAction(
        event_id=event_id if event_id is not None else
        BoboEventIDUnique().generate(),
        timestamp=timestamp if timestamp is not None else datetime.now(),
        data=data,
        process_name=process_name,
        pattern_name=pattern_name,
        action_name=action_name,
        success=success)


def block(group: str = "group",
          call: Callable = lambda e, h: e.data,
          strict: bool = False,
          loop: bool = False,
          negated: bool = False,
          optional: bool = False) -> BoboPatternBlock:
    return BoboPatternBlock(
        group=group,
        predicates=[BoboPredicateCall(call=call)],
        strict=strict,
        loop=loop,
        negated=negated,
        optional=optional)


def _lambda_event_data_equal(d: Any):
    return lambda e, h: e.data == d


def pattern(
        name: str = "pattern",
        data_blocks: List[Any] = None,
        data_pres: List[Any] = None,
        data_halts: List[Any] = None) -> BoboPattern:
    if data_blocks is None:
        data_blocks = [1]

    if data_pres is None:
        data_pres = ["p1"]

    if data_halts is None:
        data_halts = ["h1"]

    blocks: List[BoboPatternBlock] = []
    for i in range(len(data_blocks)):
        blocks.append(block(
            group=str(i + 1),
            call=_lambda_event_data_equal(data_blocks[i])))

    preconditions: List[BoboPredicate] = []
    for i in range(len(data_pres)):
        preconditions.append(BoboPredicateCall(
            call=_lambda_event_data_equal(data_pres[i])))

    haltconditions: List[BoboPredicate] = []
    for i in range(len(data_halts)):
        haltconditions.append(BoboPredicateCall(
            call=_lambda_event_data_equal(data_halts[i])))

    return BoboPattern(
        name=name,
        blocks=blocks,
        preconditions=preconditions,
        haltconditions=haltconditions)


def predicate(call: Callable = lambda e, h: True):
    return BoboPredicateCall(call=call)


def process(
        name: str = "process",
        data: Any = None,
        patterns: List[BoboPattern] = None,
        action: BoboAction = None):
    return BoboProcess(
        name=name,
        datagen=lambda p, h: data,
        patterns=patterns if patterns is not None else [],
        action=action)
