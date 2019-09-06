from bobocep.receiver.bobo_receiver import BoboReceiver
from bobocep.receiver.generators.bobo_null_data import BoboNullData
from bobocep.setup.task.bobo_task import BoboTask


class BoboNullDataGenerator(BoboTask):
    """
    A generator that periodically sends copies of some arbitrary data
    (i.e. *null data*) to a BoboReceiver instance.

    :param receiver: The data receiver to which null events are sent.
    :type receiver: BoboReceiver

    :param null_data: The null data to send.
    :type null_data: BoboNullData
    """

    def __init__(self,
                 receiver: BoboReceiver,
                 null_data: BoboNullData) -> None:
        super().__init__()

        self.receiver = receiver
        self.null_data = null_data
        self._active = False

    def _loop(self) -> None:
        if self._active:
            self.receiver.add_data(self.null_data.get_null_data())

    def activate(self) -> None:
        """
        Activates the null data generator.
        """

        with self._lock:
            self._active = True

    def deactivate(self) -> None:
        """
        Deactivates the null data generator.
        """

        with self._lock:
            self._active = False

    def _setup(self) -> None:
        """"""

    def _cancel(self) -> None:
        """"""
