from json import loads, dumps

from bobocep import BoboError
from bobocep.cep import BoboJSONable
from bobocep.cep.event import BoboHistory


class BoboRunTupleError(BoboError):
    """
    A run tuple error.
    """


class BoboRunTuple(BoboJSONable):
    """
    Represents the state of a run.
    """

    RUN_ID = "run_id"
    PHENOMENON_NAME = "phenomenon_name"
    PATTERN_NAME = "pattern_name"
    BLOCK_INDEX = "block_index"
    HISTORY = "history"

    def __init__(self,
                 run_id: str,
                 phenomenon_name: str,
                 pattern_name: str,
                 block_index: int,
                 history: BoboHistory):
        super().__init__()

        # TODO validation

        self._run_id: str = run_id
        self._phenomenon_name: str = phenomenon_name
        self._pattern_name: str = pattern_name
        self._block_index: int = block_index
        self._history: BoboHistory = history

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def phenomenon_name(self) -> str:
        return self._phenomenon_name

    @property
    def pattern_name(self) -> str:
        return self._pattern_name

    @property
    def block_index(self) -> int:
        return self._block_index

    @property
    def history(self) -> BoboHistory:
        return self._history

    def to_json_str(self) -> str:
        return dumps({
            self.RUN_ID: self.run_id,
            self.PHENOMENON_NAME: self.phenomenon_name,
            self.PATTERN_NAME: self.pattern_name,
            self.BLOCK_INDEX: self.block_index,
            self.HISTORY: self.history
        }, default=lambda o: o.to_json_str())

    @staticmethod
    def from_json_str(j: str) -> 'BoboRunTuple':
        return BoboRunTuple.from_dict(loads(j))

    @staticmethod
    def from_dict(d: dict) -> 'BoboRunTuple':
        return BoboRunTuple(
            run_id=d[BoboRunTuple.RUN_ID],
            phenomenon_name=d[BoboRunTuple.PHENOMENON_NAME],
            pattern_name=d[BoboRunTuple.PATTERN_NAME],
            block_index=d[BoboRunTuple.BLOCK_INDEX],
            history=BoboHistory.from_json_str(d[BoboRunTuple.HISTORY])
        )
