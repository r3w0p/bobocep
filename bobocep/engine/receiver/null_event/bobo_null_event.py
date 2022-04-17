from abc import ABC, abstractmethod
from typing import Union

from bobocep.events.bobo_event import BoboEvent


class BoboNullEvent(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def maybe_generate(self, event_id: str) -> Union[BoboEvent, None]:
        """"""
