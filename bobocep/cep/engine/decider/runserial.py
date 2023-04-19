# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
A serializable representation of a run.
"""

from json import loads, dumps

from bobocep import BoboError
from bobocep.bobocep import BoboJSONable
from bobocep.cep.event import BoboHistory

_EXC_RUN_ID_LEN = "run ID must have a length greater than 0"
_EXC_PHENOM_LEN = "phenomenon name must have a length greater than 0"
_EXC_INDEX = "block index must be greater than 1"
_EXC_HISTORY_LEN = "history must have at least 1 event"


class BoboRunSerialError(BoboError):
    """
    A run serial error.
    """


class BoboRunSerial(BoboJSONable):
    """
    Represents the state of a run and is designed to be serializable.
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
        """
        :param run_id: An ID for the run.
        :param phenomenon_name: A phenomenon name associated with the run.
        :param pattern_name: A pattern name associated with the run.
        :param block_index: An index which indicates where in the pattern
            to start the run.
        :param history: A history of events for the run.

        :raises BoboRunError: Run ID length is equal to 0.
        :raises BoboRunError: Process name length is equal to 0.
        :raises BoboRunError: Block index is less than 1.
        :raises BoboRunError: History does not have enough events in it
            to cover all blocks up to the block index.
        """
        super().__init__()

        if len(run_id) == 0:
            raise BoboRunSerialError(_EXC_RUN_ID_LEN)

        if len(phenomenon_name) == 0:
            raise BoboRunSerialError(_EXC_PHENOM_LEN)

        if block_index < 1:
            raise BoboRunSerialError(_EXC_INDEX)

        if history.size() < 1:
            raise BoboRunSerialError(_EXC_HISTORY_LEN)

        self._run_id: str = run_id
        self._phenomenon_name: str = phenomenon_name
        self._pattern_name: str = pattern_name
        self._block_index: int = block_index
        self._history: BoboHistory = history

    @property
    def run_id(self) -> str:
        """
        :return: The run ID.
        """
        return self._run_id

    @property
    def phenomenon_name(self) -> str:
        """
        :return: The phenomenon name associated with the run.
        """
        return self._phenomenon_name

    @property
    def pattern_name(self) -> str:
        """
        :return: The pattern name associated with the run.
        """
        return self._pattern_name

    @property
    def block_index(self) -> int:
        """
        :return: The current block index of the run.
        """
        return self._block_index

    @property
    def history(self) -> BoboHistory:
        """
        :return: The run history.
        """
        return self._history

    def to_json_dict(self) -> dict:
        """
        :return: A JSON `dict` representation of the run.
        """
        return {
            self.RUN_ID: self.run_id,
            self.PHENOMENON_NAME: self.phenomenon_name,
            self.PATTERN_NAME: self.pattern_name,
            self.BLOCK_INDEX: self.block_index,
            self.HISTORY: self.history
        }

    def to_json_str(self) -> str:
        """
        :return: A JSON `str` representation of the run.
        """
        return dumps(self.to_json_dict(), default=lambda o: o.to_json_str())

    @staticmethod
    def from_json_str(j: str) -> 'BoboRunSerial':
        """
        :param j: A JSON `str` representation of the event.

        :return: A new instance of the run serial.
        """
        return BoboRunSerial.from_json_dict(loads(j))

    @staticmethod
    def from_json_dict(d: dict) -> 'BoboRunSerial':
        """
        :param d: A JSON `dict` representation of the event.

        :return: A new instance of the run serial.
        """
        return BoboRunSerial(
            run_id=d[BoboRunSerial.RUN_ID],
            phenomenon_name=d[BoboRunSerial.PHENOMENON_NAME],
            pattern_name=d[BoboRunSerial.PATTERN_NAME],
            block_index=d[BoboRunSerial.BLOCK_INDEX],
            history=BoboHistory.from_json_str(d[BoboRunSerial.HISTORY])
        )

    def __str__(self) -> str:
        """
        :return: A JSON `str` representation of the run.
        """
        return self.to_json_str()
