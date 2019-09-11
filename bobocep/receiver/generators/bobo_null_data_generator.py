from bobocep.receiver.bobo_receiver import BoboReceiver
from bobocep.receiver.generators.data.bobo_null_data import BoboNullData
from bobocep.setup.task.bobo_task import BoboTask


class BoboNullDataGenerator(BoboTask):
    """
    A generator that periodically sends copies of some arbitrary data
    (i.e. *null data*) to a BoboReceiver instance.

    :param receiver: The data receiver to which null events are sent.
    :type receiver: BoboReceiver

    :param null_data: The null data to send.
    :type null_data: BoboNullData

    :param active: Whether task should start in an active state,
                   defaults to True.
    :type active: bool, optional
    """

    def __init__(self,
                 receiver: BoboReceiver,
                 null_data: BoboNullData,
                 active: bool = True) -> None:
        super().__init__(active=active)

        self.receiver = receiver
        self.null_data = null_data

    def _loop(self) -> None:
        self.receiver.add_data(self.null_data.get_null_data())

    def _setup(self) -> None:
        """"""

    def _cancel(self) -> None:
        """"""
