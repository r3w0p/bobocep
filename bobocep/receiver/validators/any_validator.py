from bobocep.receiver.validators.bobo_validator import \
    BoboValidator


class AnyValidator(BoboValidator):
    """A validator that accepts any data."""

    def __init__(self) -> None:
        super().__init__()

    def validate(self, data) -> bool:
        return True
