from bobocep.receiver.validators.bobo_validator import \
    BoboValidator


class StrDictValidator(BoboValidator):
    """A validator that checks whether data is a dict, where both the keys and
    values are of type str.

    :param min_length: The minimum length for strings, defaults to 0.
    :type min_length: int, optional
    """

    def __init__(self, min_length: int = 0) -> None:
        super().__init__()

        self._min_length = max(0, min_length)

    def validate(self, data) -> bool:
        if type(data) is not dict:
            return False

        for key, value in data.items():
            if type(key) is not str or type(value) is not str:
                return False

            if len(key) < self._min_length or len(value) < self._min_length:
                return False

        return True
