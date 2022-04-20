# Copyright (c) The BoboCEP Authors
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License v3.0.

from abc import ABC, abstractmethod


class BoboEngineTask(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def update(self) -> None:
        """"""
