from bobocep.receiver.validators.bobo_validator import \
    BoboValidator


class StrValidator(BoboValidator):
    """A validator that checks whether data is of type str.

    :param min_length: The minimum length for strings, defaults to 0.
    :type min_length: int, optional
    """

    def __init__(self, min_length: int = 0) -> None:
        super().__init__()

        self._min_length = max(0, min_length)

    def validate(self, data) -> bool:
        if type(data) is str and len(data) >= self._min_length:
            return True
        return False
