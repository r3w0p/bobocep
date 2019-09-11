from bobocep.receiver.generators.data.bobo_null_data import BoboNullData


class BoboNullDataNone(BoboNullData):
    """
    Null data class that always returns None.
    """

    def __init__(self) -> None:
        super().__init__()

    def get_null_data(self):
        return None
