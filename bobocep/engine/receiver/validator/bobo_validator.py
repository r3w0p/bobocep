# Copyright (c) 2022 The BoboCEP Authors
# The following code can be redistributed and/or modified
# under the terms of the GNU General Public License v3.0.

from abc import ABC, abstractmethod


class BoboValidator(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def is_valid(self, entity) -> bool:
        """"""
