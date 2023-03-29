# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Forwarder publish-subscribe classes.
"""

from abc import ABC, abstractmethod

from bobocep.cep.event import BoboEventAction


class BoboForwarderSubscriber(ABC):
    """
    A forwarder subscriber interface.
    """

    @abstractmethod
    def on_forwarder_update(self, event: BoboEventAction):
        """"""


class BoboForwarderPublisher(ABC):
    """
    A forwarder publisher interface.
    """

    @abstractmethod
    def subscribe(self, subscriber: BoboForwarderSubscriber):
        """
        :param subscriber: Subscriber to add to list.
        """