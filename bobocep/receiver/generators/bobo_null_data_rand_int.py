from random import randint

from bobocep.receiver.generators.bobo_null_data import BoboNullData


class BoboNullDataRandInt(BoboNullData):
    """
    Null data class that generates a random int within a given range.

    :param imin: The minimum possible int value.
    :type imin: int

    :param imax: The maximum possible int value.
    :type imax: int

    :raises RuntimeError: Value of imin must be lower than imax.
    """

    def __init__(self, imin: int, imax: int) -> None:
        super().__init__()

        if imin >= imax:
            raise RuntimeError("Value of imin {} must be lower than imax {}."
                               .format(imin, imax))

        self._imin = imin
        self._imax = imax

    def get_null_data(self):
        return randint(self._imin, self._imax)
