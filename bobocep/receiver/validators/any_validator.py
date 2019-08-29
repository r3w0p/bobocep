from bobocep.receiver.validators.abstract_validator import \
    AbstractValidator


class AnyValidator(AbstractValidator):
    """A validator that accepts any data."""

    def __init__(self) -> None:
        super().__init__()

    def validate(self, data) -> bool:
        return True
