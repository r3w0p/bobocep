# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from typing import Callable, List, Any, Optional

from bobocep.cep.action.bobo_action import BoboAction
from bobocep.cep.action.handler.bobo_action_handler import BoboActionHandler
from bobocep.cep.action.handler.bobo_action_handler_blocking import \
    BoboActionHandlerBlocking
from bobocep.cep.engine.bobo_engine import BoboEngine
from bobocep.cep.engine.decider.bobo_decider import BoboDecider
from bobocep.cep.engine.decider.bobo_decider_run_tuple import BoboDeciderRunTuple
from bobocep.cep.engine.decider.bobo_decider_subscriber import \
    BoboDeciderSubscriber
from bobocep.cep.engine.forwarder.bobo_forwarder import BoboForwarder
from bobocep.cep.engine.forwarder.bobo_forwarder_subscriber import \
    BoboForwarderSubscriber
from bobocep.cep.engine.producer.bobo_producer import BoboProducer
from bobocep.cep.engine.producer.bobo_producer_subscriber import \
    BoboProducerSubscriber
from bobocep.cep.engine.receiver.bobo_receiver import BoboReceiver
from bobocep.cep.engine.receiver.bobo_receiver_subscriber import \
    BoboReceiverSubscriber
from bobocep.cep.gen.event.bobo_gen_event import BoboGenEvent
from bobocep.cep.gen.event.bobo_gen_event_none import \
    BoboGenEventNone
from bobocep.cep.engine.receiver.validator.bobo_validator import BoboValidator
from bobocep.cep.engine.receiver.validator.bobo_validator_all import \
    BoboValidatorAll
from bobocep.cep.event.bobo_event import BoboEvent
from bobocep.cep.event.bobo_event_action import BoboEventAction
from bobocep.cep.event.bobo_event_complex import BoboEventComplex
from bobocep.cep.event.bobo_event_simple import BoboEventSimple
from bobocep.cep.event.bobo_history import BoboHistory
from bobocep.cep.gen.event_id.bobo_gen_event_id import BoboGenEventID
from bobocep.cep.gen.event_id.bobo_gen_event_id_unique import \
    BoboGenEventIDUnique
from bobocep.cep.gen.timestamp.bobo_gen_timestamp_epoch import \
    BoboGenTimestampEpoch
from bobocep.cep.process.bobo_process import BoboProcess
from bobocep.cep.process.pattern.bobo_pattern import BoboPattern
from bobocep.cep.process.pattern.bobo_pattern_block import BoboPatternBlock
from bobocep.cep.process.pattern.predicate.bobo_predicate import BoboPredicate
from bobocep.cep.process.pattern.predicate.bobo_predicate_call import \
    BoboPredicateCall


class BoboActionTrue(BoboAction):
    """An action that is always successful."""

    def __init__(self, name: str = "action"):
        super().__init__(name)

    def execute(self, event: BoboEventComplex) -> BoboEventAction:
        return BoboEventAction(
            event_id=BoboGenEventIDUnique().generate(),
            timestamp=BoboGenTimestampEpoch().generate(),
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
            event_id=BoboGenEventIDUnique().generate(),
            timestamp=BoboGenTimestampEpoch().generate(),
            data=False,
            process_name=event.process_name,
            pattern_name=event.pattern_name,
            action_name=self.name,
            success=False)


class BoboSameEveryTimeEventID(BoboGenEventID):
    """Produces the same ID string every time. Useful for testing whether
       an misc is raised on duplicate IDs."""

    def __init__(self, id_str: str = "id_str"):
        super().__init__()

        self.id_str = id_str

    def generate(self) -> str:
        return self.id_str


def event_simple(event_id: Optional[str] = None,
                 timestamp: Optional[int] = None,
                 data=None):
    return BoboEventSimple(
        event_id=event_id if event_id is not None else
        BoboGenEventIDUnique().generate(),
        timestamp=timestamp if timestamp is not None else
        BoboGenTimestampEpoch().generate(),
        data=data)


def event_complex(event_id: Optional[str] = None,
                  timestamp: Optional[int] = None,
                  data=None,
                  process_name: str = "process",
                  pattern_name: str = "pattern",
                  history: Optional[BoboHistory] = None):
    return BoboEventComplex(
        event_id=event_id if event_id is not None else
        BoboGenEventIDUnique().generate(),
        timestamp=timestamp if timestamp is not None else
        BoboGenTimestampEpoch().generate(),
        data=data,
        process_name=process_name,
        pattern_name=pattern_name,
        history=history if history is not None else
        BoboHistory(events={}))


def event_action(event_id: Optional[str] = None,
                 timestamp: Optional[int] = None,
                 data=None,
                 process_name: str = "process",
                 pattern_name: str = "pattern",
                 action_name: str = "action",
                 success: bool = True):
    return BoboEventAction(
        event_id=event_id if event_id is not None else
        BoboGenEventIDUnique().generate(),
        timestamp=timestamp if timestamp is not None else
        BoboGenTimestampEpoch().generate(),
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
        data_blocks: Optional[List[Any]] = None,
        data_pres: Optional[List[Any]] = None,
        data_halts: Optional[List[Any]] = None) -> BoboPattern:
    if data_blocks is None:
        data_blocks = [1]

    if data_pres is None:
        data_pres = ["p1"]

    if data_halts is None:
        data_halts = ["h1"]

    blocks: List[BoboPatternBlock] = []
    for i in range(len(data_blocks)):
        blocks.append(block(
            group="g{}".format(i + 1),
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
        datagen: Callable = lambda p, h: None,
        patterns: Optional[List[BoboPattern]] = None,
        action: Optional[BoboAction] = None):
    return BoboProcess(
        name=name,
        datagen=datagen,
        patterns=patterns if patterns is not None else [pattern()],
        action=action)


def receiver_sub(validator: Optional[BoboValidator] = None,
                 event_id_gen: Optional[BoboGenEventID] = None,
                 event_gen: Optional[BoboGenEvent] = None,
                 max_size: int = 255):
    receiver = BoboReceiver(
        validator=validator if validator is not None else
        BoboValidatorAll(),
        event_id_gen=event_id_gen if event_id_gen is not None else
        BoboGenEventIDUnique(),
        event_gen=event_gen if event_gen is not None else
        BoboGenEventNone(),
        max_size=max_size)

    subscriber = StubReceiverSubscriber()
    receiver.subscribe(subscriber=subscriber)

    return receiver, subscriber


class StubReceiverSubscriber(BoboReceiverSubscriber):
    def __init__(self):
        super().__init__()
        self.output: List[BoboEvent] = []

    def on_receiver_update(self, event: BoboEvent):
        self.output.append(event)


def decider_sub(processes: List[BoboProcess],
                event_id_gen: Optional[BoboGenEventID] = None,
                run_id_gen: Optional[BoboGenEventID] = None,
                max_size: int = 255):
    decider = BoboDecider(
        processes=processes,
        event_id_gen=event_id_gen if event_id_gen is not None else
        BoboGenEventIDUnique(),
        run_id_gen=run_id_gen if run_id_gen is not None else
        BoboGenEventIDUnique(),
        max_size=max_size)

    subscriber = StubDeciderSubscriber()
    decider.subscribe(subscriber=subscriber)

    return decider, subscriber


class StubDeciderSubscriber(BoboDeciderSubscriber):
    def __init__(self):
        super().__init__()
        self.halted_complete: List[BoboDeciderRunTuple] = []
        self.halted_incomplete: List[BoboDeciderRunTuple] = []
        self.updated: List[BoboDeciderRunTuple] = []

    def on_decider_update(self,
                          halted_complete: List[BoboDeciderRunTuple],
                          halted_incomplete: List[BoboDeciderRunTuple],
                          updated: List[BoboDeciderRunTuple]):
        self.halted_complete += halted_complete
        self.halted_incomplete += halted_incomplete
        self.updated += updated


def producer_sub(processes: List[BoboProcess],
                 event_id_gen: Optional[BoboGenEventID] = None,
                 max_size: int = 255):
    producer = BoboProducer(
        processes=processes,
        event_id_gen=event_id_gen if event_id_gen is not None else
        BoboGenEventIDUnique(),
        max_size=max_size)

    subscriber = StubProducerSubscriber()
    producer.subscribe(subscriber=subscriber)

    return producer, subscriber


class StubProducerSubscriber(BoboProducerSubscriber):

    def __init__(self):
        super().__init__()
        self.output: List[BoboEventComplex] = []

    def on_producer_update(self, event: BoboEventComplex):
        self.output.append(event)


def forwarder_sub(processes: List[BoboProcess],
                  handler: Optional[BoboActionHandler] = None,
                  event_id_gen: Optional[BoboGenEventID] = None,
                  max_size: int = 255):
    forwarder = BoboForwarder(
        processes=processes,
        handler=handler if handler is not None else
        BoboActionHandlerBlocking(max_size=max_size),
        event_id_gen=event_id_gen if event_id_gen is not None else
        BoboGenEventIDUnique(),
        max_size=max_size)

    subscriber = StubForwarderSubscriber()
    forwarder.subscribe(subscriber=subscriber)

    return forwarder, subscriber


class StubForwarderSubscriber(BoboForwarderSubscriber):

    def __init__(self):
        super().__init__()
        self.output: List[BoboEventAction] = []

    def on_forwarder_update(self, event: BoboEventAction):
        self.output.append(event)


def engine_subs(processes: List[BoboProcess],
                validator: Optional[BoboValidator] = None,
                event_id_gen: Optional[BoboGenEventID] = None,
                event_gen: Optional[BoboGenEvent] = None,
                run_id_gen: Optional[BoboGenEventID] = None,
                handler: Optional[BoboActionHandler] = None,
                times_receiver: int = 0,
                times_decider: int = 0,
                times_producer: int = 0,
                times_forwarder: int = 0,
                early_stop: bool = True,
                max_size: int = 255):
    rec, rec_sub = receiver_sub(
        validator=validator,
        event_id_gen=event_id_gen,
        event_gen=event_gen,
        max_size=max_size)

    dec, dec_sub = decider_sub(
        processes=processes,
        event_id_gen=event_id_gen,
        run_id_gen=run_id_gen,
        max_size=max_size)

    pro, pro_sub = producer_sub(
        processes=processes,
        event_id_gen=event_id_gen,
        max_size=max_size)

    fwd, fwd_sub = forwarder_sub(
        processes=processes,
        handler=handler,
        event_id_gen=event_id_gen,
        max_size=max_size)

    engine = BoboEngine(
        receiver=rec,
        decider=dec,
        producer=pro,
        forwarder=fwd,
        times_receiver=times_receiver,
        times_decider=times_decider,
        times_producer=times_producer,
        times_forwarder=times_forwarder,
        early_stop=early_stop)

    return engine, rec_sub, dec_sub, pro_sub, fwd_sub
