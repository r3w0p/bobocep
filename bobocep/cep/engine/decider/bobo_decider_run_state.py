from json import dumps, loads

from bobocep.cep.event.bobo_history import BoboHistory
from bobocep.misc.bobo_jsonable import BoboJSONable


class BoboDeciderRunState(BoboJSONable):
    """A class that represents the current state of a run."""

    PROCESS_NAME = "process_name"
    PATTERN_NAME = "pattern_name"
    BLOCK_INDEX = "block_index"
    HISTORY = "history"

    def __init__(self,
                 process_name: str,
                 pattern_name: str,
                 block_index: int,
                 history: BoboHistory):
        super().__init__()

        self._process_name: str = process_name
        self._pattern_name: str = pattern_name
        self._block_index: int = block_index
        self._history: BoboHistory = history

    @property
    def process_name(self) -> str:
        return self._process_name

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
            self.PROCESS_NAME: self.process_name,
            self.PATTERN_NAME: self.pattern_name,
            self.BLOCK_INDEX: self.block_index,
            self.HISTORY: self.history
        }, default=lambda o: o.to_json_str())

    @staticmethod
    def from_json_str(j: str) -> 'BoboDeciderRunState':
        return BoboDeciderRunState.from_dict(loads(j))

    @staticmethod
    def from_dict(d: dict) -> 'BoboDeciderRunState':
        return BoboDeciderRunState(
            process_name=d[BoboDeciderRunState.PROCESS_NAME],
            pattern_name=d[BoboDeciderRunState.PATTERN_NAME],
            block_index=d[BoboDeciderRunState.BLOCK_INDEX],
            history=BoboHistory.from_json_str(d[BoboDeciderRunState.HISTORY])
        )
