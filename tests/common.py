# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Various helper functions, classes, etc. that are common among test cases.
"""

# (putting dist imports first seems to solve "circular import" error...)
from bobocep.dist import *
from threading import RLock
from typing import Callable, List, Any, Optional
from bobocep.cep.event import *
from bobocep.cep.action import *
from bobocep.cep.gen import *
from bobocep.cep.phenomenon.pattern import *
from bobocep.cep.phenomenon import *
from bobocep.cep.engine.receiver import *
from bobocep.cep.engine.decider import *
from bobocep.cep.engine.producer import *
from bobocep.cep.engine.forwarder import *
from bobocep.cep.engine import *


class BoboActionTrue(BoboAction):
    """An action that is always successful."""

    def __init__(self, name: str = "action"):
        super().__init__(name)

    def execute(self, event: BoboEventComplex) -> BoboEventAction:
        return BoboEventAction(
            event_id=BoboGenEventIDUnique().generate(),
            timestamp=BoboGenTimestampEpoch().generate(),
            data=True,
            phenomenon_name=event.phenomenon_name,
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
            phenomenon_name=event.phenomenon_name,
            pattern_name=event.pattern_name,
            action_name=self.name,
            success=False)


class BoboSameEveryTimeEventID(BoboGenEventID):
    """
    Produces the same ID string every time.
    Useful for testing whether an error is raised on duplicate IDs.
    """

    def __init__(self, id_str: str = "id_str"):
        super().__init__()

        self._id_str = id_str

    def generate(self) -> str:
        return self._id_str


class BoboEventSimpleSubclass(BoboEventSimple):
    """"""


class StubReceiverSubscriber(BoboReceiverSubscriber):
    def __init__(self):
        super().__init__()
        self.output: List[BoboEvent] = []

    def on_receiver_update(self, event: BoboEvent):
        self.output.append(event)


class StubDeciderSubscriber(BoboDeciderSubscriber):
    def __init__(self):
        super().__init__()
        self.completed: List[BoboRunTuple] = []
        self.halted: List[BoboRunTuple] = []
        self.updated: List[BoboRunTuple] = []

    def on_decider_update(self,
                          completed: List[BoboRunTuple],
                          halted: List[BoboRunTuple],
                          updated: List[BoboRunTuple]):
        self.completed += completed
        self.halted += halted
        self.updated += updated


class StubProducerSubscriber(BoboProducerSubscriber):

    def __init__(self):
        super().__init__()
        self.output: List[BoboEventComplex] = []

    def on_producer_update(self, event: BoboEventComplex):
        self.output.append(event)


class StubForwarderSubscriber(BoboForwarderSubscriber):

    def __init__(self):
        super().__init__()
        self.output: List[BoboEventAction] = []

    def on_forwarder_update(self, event: BoboEventAction):
        self.output.append(event)


class StubDistributedSubscriber(BoboDistributedSubscriber):

    def __init__(self):
        super().__init__()
        self._lock: RLock = RLock()

        self._completed: List[BoboRunTuple] = []
        self._halted: List[BoboRunTuple] = []
        self._updated: List[BoboRunTuple] = []

    def on_distributed_update(self,
                              completed: List[BoboRunTuple],
                              halted: List[BoboRunTuple],
                              updated: List[BoboRunTuple]):
        with self._lock:
            self._completed += completed
            self._halted += halted
            self._updated += updated

    @property
    def completed(self):
        with self._lock:
            return self._completed

    @property
    def halted(self):
        with self._lock:
            return self._halted

    @property
    def updated(self):
        with self._lock:
            return self._updated


class BoboValidatorRejectAll(BoboValidator):
    """Validator that always rejects data."""

    def is_valid(self, data: Any) -> bool:
        """
        :return: Always returns `False`.
        """
        return False


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
                  phenomenon_name: str = "phenomenon",
                  pattern_name: str = "pattern",
                  history: Optional[BoboHistory] = None):
    return BoboEventComplex(
        event_id=event_id if event_id is not None else
        BoboGenEventIDUnique().generate(),
        timestamp=timestamp if timestamp is not None else
        BoboGenTimestampEpoch().generate(),
        data=data,
        phenomenon_name=phenomenon_name,
        pattern_name=pattern_name,
        history=history if history is not None else
        BoboHistory(events={}))


def event_action(event_id: Optional[str] = None,
                 timestamp: Optional[int] = None,
                 data=None,
                 phenomenon_name: str = "phenomenon",
                 pattern_name: str = "pattern",
                 action_name: str = "action",
                 success: bool = True):
    return BoboEventAction(
        event_id=event_id if event_id is not None else
        BoboGenEventIDUnique().generate(),
        timestamp=timestamp if timestamp is not None else
        BoboGenTimestampEpoch().generate(),
        data=data,
        phenomenon_name=phenomenon_name,
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
        data_pres = []

    if data_halts is None:
        data_halts = []

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


def phenomenon(
        name: str = "phenomenon",
        datagen: Callable = lambda p, h: None,
        patterns: Optional[List[BoboPattern]] = None,
        action: Optional[BoboAction] = None):
    return BoboPhenomenon(
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
        gen_event_id=event_id_gen if event_id_gen is not None else
        BoboGenEventIDUnique(),
        gen_timestamp=BoboGenTimestampEpoch(),
        gen_event=event_gen if event_gen is not None else
        BoboGenEventNone(),
        max_size=max_size)

    subscriber = StubReceiverSubscriber()
    receiver.subscribe(subscriber=subscriber)

    return receiver, subscriber


def decider_sub(phenomena: List[BoboPhenomenon],
                event_id_gen: Optional[BoboGenEventID] = None,
                run_id_gen: Optional[BoboGenEventID] = None,
                max_cache: int = 0,
                max_size: int = 255):
    decider = BoboDecider(
        phenomena=phenomena,
        gen_event_id=event_id_gen if event_id_gen is not None else
        BoboGenEventIDUnique(),
        gen_run_id=run_id_gen if run_id_gen is not None else
        BoboGenEventIDUnique(),
        max_cache=max_cache,
        max_size=max_size)

    subscriber = StubDeciderSubscriber()
    decider.subscribe(subscriber=subscriber)

    return decider, subscriber


def producer_sub(phenomena: List[BoboPhenomenon],
                 event_id_gen: Optional[BoboGenEventID] = None,
                 max_size: int = 255):
    producer = BoboProducer(
        phenomena=phenomena,
        gen_event_id=event_id_gen if event_id_gen is not None else
        BoboGenEventIDUnique(),
        gen_timestamp=BoboGenTimestampEpoch(),
        max_size=max_size)

    subscriber = StubProducerSubscriber()
    producer.subscribe(subscriber=subscriber)

    return producer, subscriber


def forwarder_sub(phenomena: List[BoboPhenomenon],
                  handler: Optional[BoboActionHandler] = None,
                  event_id_gen: Optional[BoboGenEventID] = None,
                  max_size: int = 255):
    forwarder = BoboForwarder(
        phenomena=phenomena,
        handler=handler if handler is not None else
        BoboActionHandlerBlocking(max_size=max_size),
        gen_event_id=event_id_gen if event_id_gen is not None else
        BoboGenEventIDUnique(),
        max_size=max_size)

    subscriber = StubForwarderSubscriber()
    forwarder.subscribe(subscriber=subscriber)

    return forwarder, subscriber


def run_simple(
        pattern: BoboPattern,
        event: BoboEvent,
        run_id: str = "run_id",
        phenomenon_name: str = "phenomenon",
        block_index: int = 1):
    return BoboRun(
        run_id=run_id,
        phenomenon_name=phenomenon_name,
        pattern=pattern,
        block_index=block_index,
        history=BoboHistory({
            pattern.blocks[0].group: [event]
        })
    )


def run_tuple(
        run_id: str = "run_id",
        phenomenon_name: str = "phenomenon_name",
        pattern_name: str = "pattern_name",
        block_index: int = 1,
        history: BoboHistory = BoboHistory({})):
    return BoboRunTuple(
        run_id=run_id,
        phenomenon_name=phenomenon_name,
        pattern_name=pattern_name,
        block_index=block_index,
        history=history
    )


def engine_subs(phenomena: List[BoboPhenomenon],
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
        phenomena=phenomena,
        event_id_gen=event_id_gen,
        run_id_gen=run_id_gen,
        max_size=max_size)

    pro, pro_sub = producer_sub(
        phenomena=phenomena,
        event_id_gen=event_id_gen,
        max_size=max_size)

    fwd, fwd_sub = forwarder_sub(
        phenomena=phenomena,
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
