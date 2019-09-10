from abc import ABC, abstractmethod


class IDistOutgoingSubscriber(ABC):

    @abstractmethod
    def on_sync(self) -> None:
        """When the :code:`bobocep` instance has synchronised with other
        instances."""
