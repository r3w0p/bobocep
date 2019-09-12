from bobocep.receiver.generators.data.bobo_null_data import BoboNullData


class BoboNullDataStatic(BoboNullData):
    """
    Null data class that always returns some static data.
    """

    def __init__(self, data) -> None:
        super().__init__()

        self._data = data

    def get_null_data(self):
        return self._data
