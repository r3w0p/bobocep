from src.cep.event.bobo_history import BoboHistory
from src.misc.bobo_jsonable import BoboJSONable


class BoboDeciderRunTuple(BoboJSONable):

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

    def to_json_str(self) -> dict:
        return {
            self.PROCESS_NAME: self.process_name,
            self.PATTERN_NAME: self.pattern_name,
            self.BLOCK_INDEX: self.block_index,
            self.HISTORY: self.history.to_json_str()
        }

    @staticmethod
    def from_json_str(d: dict) -> 'BoboDeciderRunTuple':
        BoboDeciderRunTuple._validate_dict(d, [
            (BoboDeciderRunTuple.PROCESS_NAME, str),
            (BoboDeciderRunTuple.PATTERN_NAME, str),
            (BoboDeciderRunTuple.BLOCK_INDEX, int),
            (BoboDeciderRunTuple.HISTORY, dict)
        ])

        return BoboDeciderRunTuple(
            process_name=d[BoboDeciderRunTuple.PROCESS_NAME],
            pattern_name=d[BoboDeciderRunTuple.PATTERN_NAME],
            block_index=d[BoboDeciderRunTuple.BLOCK_INDEX],
            history=BoboHistory.from_json_str(d[BoboDeciderRunTuple.HISTORY])
        )
